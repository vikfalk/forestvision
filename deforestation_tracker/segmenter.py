import numpy as np

def segment(img_array: np.array, model, threshold = 0.7) -> np.array:
    """Takes a scaled image array, predicts its rainforest segmentation, converts it
    to black and white according to a threshold. Returns a (512, 512) img_array.
    """
    predicted_img_array = model.predict(np.expand_dims(img_array, axis=0))[0, :, :, 0]
    black_white_img_array = (predicted_img_array > threshold).astype(np.uint8) * 255
    return black_white_img_array
