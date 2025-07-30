# Scorpia-Pixel

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)

Scorpia-Pixel is a lightweight Python package for image manipulation and processing, created as a personal project to explore and learn the fundamentals of computer vision. This package represents my journey into understanding image processing techniques through practical implementation.

## Project Purpose

This project is my personal playground for learning image processing with Python. I'm building filters and transformations from scratch to really understand how computer vision works. You're welcome to use it, but just know—I'm mainly doing this to teach myself
## Features

Scorpia-Pixel v0.1.0 includes the following core features:

- **Color Inversion**: Transform images to their negative counterparts with a single function call
- **Image Blurring**: Apply different blur techniques to images
  - Box blur: Simple averaging filter for uniform blurring
  - Gaussian blur: Weighted blur that preserves edges better than box blur
- **Padding Support**: Current version supports constant (zero) padding for filter operations
- **Simple I/O Operations**: Convenient functions for loading and saving images

## Installation

### From PyPI (Recommended)

```bash
pip install scorpia-pixel
```

### From Source

```bash
git clone https://github.com/Montasar-Dridi/scorpia-pixel.git
cd scorpia-pixel
pip install -e .
```

### Requirements

- Python 3.6+
- NumPy
- Pillow (PIL)
- pytest (for running tests)

## Quick Start

Here's a simple example to get you started with Scorpia-Pixel:

```python
from pixel_core import load_image, save_image, invert_colors, blur_image

# Load an image
image = load_image("path/to/your/image.jpg")

# Apply color inversion
inverted = invert_colors(image)

# Apply Gaussian blur with kernel size 5
blurred = blur_image(image, kernel_size=5, kernel_type="gaussian")

# Save the processed images
save_image(inverted, filter_name="inverted")  # Saves as scorpia_inverted_0.png
save_image(blurred, filter_name="blurred")    # Saves as scorpia_blurred_0.png
```

## API Reference

### Image I/O

#### `load_image(path: str) -> np.ndarray`

Loads an image from the specified path and returns it as a NumPy array.

**Parameters:**
- `path` (str): Path to the image file

**Returns:**
- `np.ndarray`: Image as a NumPy array with shape (H, W, 3) and dtype uint8

**Raises:**
- `FileNotFoundError`: If the image file doesn't exist
- `ValueError`: If the file is not a valid image

#### `save_image(image_array: np.ndarray, output_path: str = "output_images", filter_name: str = "output") -> None`

Saves an image array to disk with an auto-incremented filename.

**Parameters:**
- `image_array` (np.ndarray): Image as a NumPy array with shape (H, W, 3) and dtype uint8
- `output_path` (str, optional): Directory to save the image. Defaults to "output_images"
- `filter_name` (str, optional): Name of the filter applied. Defaults to "output"

**Returns:**
- None

### Image Filters

#### `invert_colors(image_array: np.ndarray, *, in_place: bool = False) -> np.ndarray`

Inverts the colors of an image.

**Parameters:**
- `image_array` (np.ndarray): Input image with shape (H, W, 3) and dtype uint8
- `in_place` (bool, optional): If True, modifies the input array directly. Defaults to False

**Returns:**
- `np.ndarray`: Color-inverted image with the same shape and dtype as the input

#### `blur_image(image_array: np.ndarray, *, kernel_size: int = 3, kernel_type: str = "box", padding: str = "constant") -> np.ndarray`

Applies a blur filter to an image.

**Parameters:**
- `image_array` (np.ndarray): Input image with shape (H, W, 3) and dtype uint8
- `kernel_size` (int, optional): Size of the square kernel (must be odd). Defaults to 3
- `kernel_type` (str, optional): Type of kernel to use. Options: "box", "gaussian". Defaults to "box"
- `padding` (str, optional): Padding method. Currently only "constant" (zero padding) is supported. Defaults to "constant"

**Returns:**
- `np.ndarray`: Blurred image with the same shape as the input

### Utility Functions

#### `check_rgb_uint8(image_array: np.ndarray) -> None`

Validates that an image array has the correct shape and dtype.

**Parameters:**
- `image_array` (np.ndarray): Image array to validate

**Raises:**
- `TypeError`: If the image array's dtype is not uint8
- `ValueError`: If the image array's shape is not (H, W, 3)

## Project Structure

```
scorpia-pixel/
│
├── pixel_core/          # Main package directory
│   ├── __init__.py      # Exports public API functions
│   ├── filters.py       # Image filter implementations
│   └── image_utils.py   # I/O and utility functions
│
├── tests/               # Test directory
│   ├── blur_image_test.py
│   └── invert_filter_test.py
│
├── requirements.txt     # Project dependencies
├── LICENSE              # MIT License
└── README.md            # This file
```

## Development Roadmap

Scorpia-Pixel follows a structured release strategy as I continue to learn and implement new computer vision concepts:

### Current Release (v0.1.0) - Core Filters
- ✅ Color inversion
- ✅ Blur filters (box, gaussian)
- ✅ Constant padding
- ✅ Basic image I/O

### Upcoming Releases

#### v0.2.0 - Blurring & Padding Enhancements
- Additional blur techniques (median, motion, bilateral, custom kernels)
- More padding types (reflect, replicate, wrap, symmetric)

#### v0.3.0 - Transformations & Grayscale
- Grayscale conversion
- Image transformations (resize, rotate, crop)

#### v0.4.0 - Edge Detection & Effects
- Edge detection algorithms (Sobel, Laplacian, Canny)
- Brightness and contrast adjustment
- Sharpening and embossing filters

#### v1.0.0 - Stable Release
- Full documentation
- CLI support for terminal usage
- Comprehensive usage examples
- Performance benchmarking
- Code cleanup and packaging polish

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Scorpia-Pixel is developed by Montasar Dridi, a data scientist with interests in computer vision, AI, and software development. This project represents my personal journey into learning computer vision fundamentals through practical implementation.

GitHub: [https://github.com/Montasar-Dridi](https://github.com/Montasar-Dridi)
