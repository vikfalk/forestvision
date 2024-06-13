import numpy as np
from PIL import Image

def segment(img_array: np.array, model) -> np.array:
    """Takes a scaled image array, predicts its rainforest segmentation, converts it
    to black and white and crops the images white padding. Returns a numpy
    array representing the image.
    """
    # adding batch size dimension
    prediction = model.predict(np.expand_dims(img_array, axis=0))
    predicted_image_array = prediction[0]

    # converting to black and white
    threshold = 0.5
    binary_image_array = (predicted_image_array > threshold).astype(np.uint8) * 255

    # reducing dimensions
    if binary_image_array.ndim == 3 and binary_image_array.shape[-1] == 1:
        binary_image_array = binary_image_array.squeeze(-1)
    binary_image_pil = Image.fromarray(binary_image_array, mode='L') # 'L' mode is for (8-bit pixels, black and white)

    # detect white padding/box and cropping
    bbox = binary_image_pil.getbbox()
    cropped_img = binary_image_pil.crop(bbox) if bbox else binary_image_pil

    # cropped_img.save(output_path)
    cropped_img_array = np.array(cropped_img, dtype=np.uint8)
    return cropped_img_array


def segment_self(img_array: np.array, model) -> np.array:
    """Takes a scaled image array, predicts its rainforest segmentation, converts it
    to black and white and crops the images white padding. Returns a numpy
    array representing the image.
    """
    # adding batch size dimension
    prediction = model.predict(np.expand_dims(img_array, axis=0))
    prediction = prediction.reshape((512,512,1))

    # converting predicted image to black and white
    threshold = 0.7
    prediction_array = (prediction > threshold).astype(np.uint8) * 255
    prediction_array = prediction_array.astype(np.uint8)

    return prediction_array
