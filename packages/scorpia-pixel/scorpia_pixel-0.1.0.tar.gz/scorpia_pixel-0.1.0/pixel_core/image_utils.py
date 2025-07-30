import os
import numpy as np
from PIL import Image, UnidentifiedImageError


def load_image(path: str) -> np.ndarray:
    """load an image as a numpy array"""
    try:
        image = Image.open(path).convert("RGB")
        return np.asarray(image, dtype=np.uint8)
    except (FileNotFoundError):
        raise FileNotFoundError(f"File not found: {path}")
    except (UnidentifiedImageError):
        raise ValueError(f"The file at {path} is not a valid image") from UnidentifiedImageError


import os

def save_image(image_array: np.ndarray, output_path: str = "output_images", filter_name: str = "output") -> None:
    """
    Save an image with an auto-incremented, clean, and descriptive filename.

    Example filename: scorpia_invert_0.png
    """
    os.makedirs(output_path, exist_ok=True)

    index = 0
    while True:
        filename = f"scorpia_{filter_name}_{index}.png"
        full_path = os.path.join(output_path, filename)
        if not os.path.exists(full_path):
            break
        index += 1

    to_image = Image.fromarray(image_array)
    to_image.save(full_path)



def check_rgb_uint8(image_array: np.ndarray) -> None:
    if image_array.dtype != np.uint8:
        raise TypeError("image_array must have dtype uint8")
    if image_array.ndim != 3 or image_array.shape[2] != 3:
        raise ValueError("image_array must have shape (H, W, 3)")