import numpy as np
import cv2
from PIL import Image, ImageFilter, ImageColor


def bw_to_color(
    bw_image: np.ndarray, black_substitute: str, white_substitute: str
    ) -> np.ndarray:
    black_substitute_rgb = ImageColor.getcolor(black_substitute, "RGB")
    white_substitute_rgb = ImageColor.getcolor(white_substitute, "RGB")
    height, width = bw_image.shape
    color_image = np.zeros((height, width, 3), dtype=np.uint8)  # Initialize RGB image
    color_image[bw_image == 0] = black_substitute_rgb
    color_image[bw_image == 255] = white_substitute_rgb
    return color_image


def smooth_and_vectorize(array, hex_code, smoothing=9, opacity=0.5):
    '''
    Takes the model output array, smooths, colours, defines opacity,
    and makes background transparent.
    '''
    array_resized = cv2.resize(array, (512, 512))
    array_rgba = np.zeros((512, 512, 4), dtype=np.uint8)
    # Copy the grayscale values to all RGB channels
    array_rgba[:, :, 0] = array_resized
    array_rgba[:, :, 1] = array_resized
    array_rgba[:, :, 2] = array_resized
    # Set alpha channel based on white pixels
    array_rgba[:, :, 3] = np.where(array_resized == 255, 0, 255)

    image = Image.fromarray(array_rgba)
    med_img = image.filter(ImageFilter.MedianFilter(size=smoothing))

    # Convert the smoothed image to grayscale
    smoothed_image = med_img.convert("L")
    smoothed_array = np.array(smoothed_image)

    # Binarize the smoothed image (invert the binary image)
    _, binary_image = cv2.threshold(smoothed_array, 127, 255, cv2.THRESH_BINARY)
    mask = Image.fromarray(binary_image).convert("L")

    # Convert the hex code to RGB components
    hex_code = hex_code.lstrip('#')
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)
    opacity = int(opacity * 255)
    rgba = (r, g, b, opacity)
    color_img = Image.new("RGBA", image.size, rgba)

    smooth_coloured_vector = Image.composite(
        color_img,
        Image.new("RGBA", image.size, (0, 0, 0, 0)),
        mask
    )
    smooth_coloured_vector_rgba = smooth_coloured_vector.convert("RGBA")
    return smooth_coloured_vector_rgba


def overlay_vector_on_image(
    vector: np.ndarray, image: Image.Image, vector_hex_code: str
    ) -> Image.Image:
    """Paste the vector on the image with the given hex code."""
    smoothed_vector = smooth_and_vectorize(
        array=vector,
        hex_code=vector_hex_code
    )
    converted_image = (
        Image.fromarray(image).convert('RGBA')
        if isinstance(image, np.ndarray)
        else image
    )
    overlayed_image = Image.alpha_composite(
        im1=converted_image,
        im2=smoothed_vector
    )
    return overlayed_image
