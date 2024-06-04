from PIL import Image, ImageFilter
import numpy as np
import cv2

def smooth_and_vectorize(array, smoothing, hex_code, opacity):
    '''
    Takes the model output array, smooths, colours, defines opacity, and makes background transparent.
    smoothing = odd int e.g. 1, 3, 5, 7
    hex_code = str hexcode of colour e.g. #FF0000 (red)
    opacity = float between 0 - 1 
    '''
    array_resized = cv2.resize(array, (512, 512))

    # Convert numpy array to PIL Image
    array_rgba = np.zeros((512, 512, 4), dtype=np.uint8)
    array_rgba[:, :, 0] = array_resized  # Copy the grayscale values to all RGB channels
    array_rgba[:, :, 1] = array_resized
    array_rgba[:, :, 2] = array_resized
    array_rgba[:, :, 3] = np.where(array_resized == 255, 0, 255)  # Set alpha channel based on white pixels
    
    image = Image.fromarray(array_rgba)

    # Apply Median Filter
    med_img = image.filter(ImageFilter.MedianFilter(size=smoothing))

    # Convert the smoothed image to grayscale
    smoothed_image = med_img.convert("L")

    # Convert to numpy array
    smoothed_array = np.array(smoothed_image)

    # Binarize the smoothed image (invert the binary image)
    _, binary_image = cv2.threshold(smoothed_array, 127, 255, cv2.THRESH_BINARY)

    # Create a mask from the binary image
    mask = Image.fromarray(binary_image).convert("L")

    # Create an RGBA image with the specified color
    
    #Convert hex into RGB
    hex_code = hex_code.lstrip('#')

    # Convert the hex code to RGB components
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)
    
    opacity = int(opacity * 255)
    rgba = (r, g, b, opacity)

    color_img = Image.new("RGBA", image.size, rgba)

    # Composite the color image with the mask
    smooth_coloured_vector = Image.composite(color_img, Image.new("RGBA", image.size, (0, 0, 0, 0)), mask)
    
    return smooth_coloured_vector
    
    # Save as PNG
    smooth_coloured_vector.save("smoothed_red.png")
    
def overlay_vector_on_mask(vector, mask):
    mask_rgba= mask.convert("RGBA")
    return Image.alpha_composite(mask_rgba, vector)