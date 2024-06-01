from PIL import Image, ImageFilter
import numpy as np
import cv2

def smooth_and_vectorize(array, smoothing, colour_and_opacity):
    '''
    Takes the model output array, smooths, colours, defines opacity, and makes background transparent.
    smoothing = odd int e.g. 1, 3, 5, 7
    colour_and_opacity = tuple with RGBA e.g. for red with full opacity -> (255, 0, 0, 255)
    '''
    # Convert numpy array to PIL Image
    array_rgba = np.zeros((512, 512, 4), dtype=np.uint8)
    array_rgba[:, :, 0] = array  # Copy the grayscale values to all RGB channels
    array_rgba[:, :, 1] = array
    array_rgba[:, :, 2] = array
    array_rgba[:, :, 3] = np.where(array == 255, 0, 255)  # Set alpha channel based on white pixels
    
    image = Image.fromarray(array_rgba)

    # Apply Median Filter
    med_img = image.filter(ImageFilter.MedianFilter(size=smoothing))

    # Convert the smoothed image to grayscale
    smoothed_image = med_img.convert("L")

    # Convert to numpy array
    smoothed_array = np.array(smoothed_image)

    # Binarize the smoothed image (invert the binary image)
    _, binary_image = cv2.threshold(smoothed_array, 127, 255, cv2.THRESH_BINARY_INV)

    # Create a mask from the binary image
    mask = Image.fromarray(binary_image).convert("L")

    # Create an RGBA image with the specified color
    color = (255, 0, 0, 255)  # Red color with full opacity
    color_img = Image.new("RGBA", image.size, color)

    # Composite the color image with the mask
    smooth_coloured_vector = Image.composite(color_img, Image.new("RGBA", image.size, (0, 0, 0, 0)), mask)
    
    return smooth_coloured_vector
    
    # Save as PNG
    smooth_coloured_vector.save("smoothed_red.png")