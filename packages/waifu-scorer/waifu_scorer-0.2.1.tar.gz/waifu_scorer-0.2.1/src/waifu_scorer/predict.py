import contextlib
import logging
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import ExifTags, Image
from transformers import CLIPModel, CLIPProcessor

from .mlp import MLP

ws_repo = "Eugeoter/waifu-scorer-v3"
logger = logging.getLogger("WaifuScorer")


def rotate_image_straight(image: Image.Image) -> Image.Image:
    with contextlib.suppress(Exception):
        if exif := image.getexif():
            orientation_tag = {v: k for k, v in ExifTags.TAGS.items()}["Orientation"]
            orientation = exif.get(orientation_tag)
            if degree := {
                3: 180,
                6: 270,
                8: 90,
            }.get(orientation):
                image = image.rotate(degree, expand=True)
    return image


def fill_transparency(image: Image.Image | np.ndarray, bg_color: tuple[int, int, int] = (255, 255, 255)):
    r"""
    Fill the transparent part of an image with a background color.
    Please pay attention that this function doesn't change the image type.
    """
    if isinstance(image, Image.Image):
        # Only process if image has transparency
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
            alpha = image.convert("RGBA").split()[-1]

            # Create a new background image of our matt color.
            # Must be RGBA because paste requires both images have the same format
            # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
            bg = Image.new("RGBA", image.size, (*bg_color, 255))
            bg.paste(image, mask=alpha)
            return bg
        return image
    if isinstance(image, np.ndarray):
        if image.shape[2] == 4:  # noqa: PLR2004
            alpha = image[:, :, 3]
            bg = np.full_like(image, (*bg_color, 255))
            bg[:, :, :3] = image[:, :, :3]
            return bg
        return image
    return None


def download_from_url(url: str):
    from huggingface_hub import hf_hub_download

    split = url.split("/")
    username, repo_id, model_name = split[-3], split[-2], split[-1]
    return hf_hub_download(f"{username}/{repo_id}", model_name)


def convert_to_rgb(image: Image.Image | np.ndarray, bg_color: tuple[int, int, int] = (255, 255, 255)):
    r"""
    Convert an image to RGB mode and fix transparency conversion if needed.
    """
    image = fill_transparency(image, bg_color)
    if isinstance(image, Image.Image):
        return image.convert("RGB")
    return image[:, :, :3] if isinstance(image, np.ndarray) else None


def repo2path(model_repo_and_path: str, *, use_safetensors: bool = True):
    ext = ".safetensors" if use_safetensors else ".pth"
    p = Path(model_repo_and_path)
    if p.is_file():
        model_path = p
    elif p.is_dir():
        model_path = p / f"model{ext}"
    elif model_repo_and_path == ws_repo:
        model_path = Path(model_repo_and_path) / f"model{ext}"
    else:
        msg = f"Invalid model_repo_and_path: {model_repo_and_path}"
        raise ValueError(msg)
    return model_path.as_posix()


def load_model(
    model_path: str | None = None,
    input_size: int = 768,
    device: str = "cuda",
    dtype: None | str = None,
):
    model = MLP(input_size=input_size)
    if model_path:
        if model_path.endswith(".safetensors"):
            from safetensors.torch import load_file

            state_dict = load_file(model_path)
        else:
            state_dict = torch.load(model_path, map_location=device, weights_only=True)
        model.load_state_dict(state_dict)
        model.to(device)
    if dtype:
        model = model.to(dtype=dtype)
    return model


class WaifuScorer:
    def __init__(
        self,
        model_path: str | None = None,
        device: str = "cuda",
        *,
        verbose: bool = False,
        clip_model: Any = None,
        clip_processor: Any = None,
    ):
        self.verbose = verbose
        self.logger = logging.getLogger(self.__class__.__name__)
        if model_path is None:  # auto
            model_path = repo2path(
                ws_repo,
                use_safetensors=True,
            )
            if self.verbose:
                self.logger.info(
                    "model path not set, switch to default: `%s`",
                    model_path,
                )
        if not Path(model_path).is_file():
            self.logger.info(
                "model path not found in local, trying to download from url: %s",
                model_path,
            )
            model_path = download_from_url(model_path)

        self.logger.info(
            "loading pretrained model from `%s`",
            model_path,
        )
        self.mlp = load_model(model_path, input_size=768, device=device)
        if clip_model is not None and clip_processor is not None:
            self.clip = clip_model
            self.preprocess = clip_processor
        else:
            self.clip, self.preprocess = load_clip_models(device=device)
        self.device = self.mlp.device
        self.dtype = self.mlp.dtype
        self.mlp.eval()

    @torch.no_grad()
    def __call__(
        self,
        inputs: list[Image.Image | torch.Tensor | Path | str],
    ) -> list[float]:
        return self.predict(inputs)

    @torch.no_grad()
    def predict(
        self,
        inputs: list[Image.Image | torch.Tensor | Path | str],
    ) -> list[float]:
        img_embs = self.encode_inputs(inputs)
        return self.inference(img_embs)

    @torch.no_grad()
    def inference(self, img_embs: torch.Tensor) -> list[float]:
        img_embs = img_embs.to(device=self.device, dtype=self.dtype)
        predictions = self.mlp(img_embs)
        return predictions.clamp(0, 10).cpu().numpy().reshape(-1).tolist()

    def get_image(self, img_path: str | Path) -> Image.Image:
        image = Image.open(img_path)
        image = convert_to_rgb(image)
        return rotate_image_straight(image)

    def encode_inputs(
        self,
        inputs: list[Image.Image | torch.Tensor | Path | str],
    ) -> torch.Tensor:
        r"""
        Encode inputs to image embeddings.
        """
        if isinstance(inputs, (Image.Image, torch.Tensor, str, Path)):
            inputs = [inputs]

        image_or_tensors = [self.get_image(inp) if isinstance(inp, (str, Path)) else inp for inp in inputs]
        image_idx = [i for i, img in enumerate(image_or_tensors) if isinstance(img, Image.Image)]
        batch_size = len(image_idx)
        if batch_size > 0:
            images = [image_or_tensors[i] for i in image_idx]
            if batch_size == 1:
                images *= 2
            img_embs = encode_images(
                images,
                self.clip,
                self.preprocess,
                device=self.device,
            )
            if batch_size == 1:
                img_embs = img_embs[:1]
            for i, idx in enumerate(image_idx):
                image_or_tensors[idx] = img_embs[i]
        return torch.stack(image_or_tensors, dim=0)


def load_clip_models(device: str = "cuda"):
    model_name = "openai/clip-vit-large-patch14"
    clip_model = CLIPModel.from_pretrained(model_name).to(device)
    processor = CLIPProcessor.from_pretrained(model_name, use_fast=False)
    return clip_model, processor


def normalized(a: torch.Tensor, order: int = 2, dim: int = -1):
    l2 = a.norm(order, dim, keepdim=True)
    l2[l2 == 0] = 1
    return a / l2


def encode_images(
    images: list[Image.Image],
    clip_model: CLIPModel,
    preprocess: CLIPProcessor,
    device: str = "cuda",
) -> torch.Tensor:
    if isinstance(images, Image.Image):
        images = [images]
    inputs = preprocess(images=images, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        image_features = clip_model.get_image_features(**inputs)
    return normalized(image_features).cpu().float()
