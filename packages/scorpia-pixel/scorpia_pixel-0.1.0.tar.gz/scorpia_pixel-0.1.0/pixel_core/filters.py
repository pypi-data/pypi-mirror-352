import numpy as np
from pixel_core.image_utils import load_image, save_image, check_rgb_uint8


def invert_colors(image_array: np.ndarray, *, in_place: bool = False) -> np.ndarray:
    """
    invert colors of an image

    Parameters
    ----------
    image_array: np.ndarray
        input image, dtype uint8, shape (H, w, 3).
    in_place: bool, default False
        if True, modify the input image directly; if false, modify a copy of the input image

    Returns:
    --------
    np.ndarray
    Color inverted image with the same shape and dtype as "image_array"
    """
    check_rgb_uint8(image_array)

    if in_place:
        np.subtract(255, image_array, out=image_array)
        return image_array
    else:
        return 255 - image_array
    

def blur_image(image_array:np.ndarray, *,kernel_size: int = 3,kernel_type: str = "box" ,padding: str = "constant") -> np.ndarray:
    """
    Apply a blur filter to an image.

    Parameters
    ----------
    image_array : np.ndarray
        Input image. Shape (H, W) for grayscale or (H, W, 3) for RGB. Dtype float32 or uint8.
    kernel_size : int, default=3
        Size of the square kernel (must be odd).
    kernel_type : str, default='box'
        Type of kernel to use. Currently only 'box' is supported.
    padding : str, default='constant'
        Padding method. Currently only 'constant' (zero padding) is supported.

    Returns
    -------
    np.ndarray
        Blurred image with the same shape as 'image_array'.
"""
    check_rgb_uint8(image_array)
    if kernel_size % 2 == 0:
        raise ValueError("Kernel_size must be an odd integer")
    
    pad = kernel_size // 2
    blurred_array = np.zeros_like(image_array, dtype=np.float32) # initialize empty array

    if padding.lower() == "constant":
        padded_array = np.pad(image_array, ((pad, pad), (pad, pad), (0,0)), mode="constant", constant_values=0)
    
    if kernel_type.lower() == "box":
        kernel = np.ones((kernel_size, kernel_size)) / (kernel_size * kernel_size)
    elif kernel_type.lower() == "gaussian":
        sigma = kernel_size / 6
        kernel_center = pad
        kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)

        for horizantal in range(kernel_size):
            for vertical in range(kernel_size):
                x = horizantal - kernel_center
                y = vertical - kernel_center
                kernel[horizantal, vertical] = np.exp(-(x**2 + y**2) / (2 * sigma**2))
        kernel /= np.sum(kernel)
                

    for channel in range(3):
        for height in range(image_array.shape[0]):
            for width in range(image_array.shape[1]):
                region = padded_array[height:height+kernel_size, width:width+kernel_size, channel]
                blurred_pixel = np.sum(region * kernel)
                blurred_array[height, width, channel] = blurred_pixel

    blurred_array = np.clip(blurred_array, 0, 255).astype(np.uint8)
    return blurred_array