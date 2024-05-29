from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np

def path_constructor(image_name_without_ending="after_resized"):
    """Hard coded function that returns paths to pulls in local .tiff file and output a .png file."""
    input_file_ending = ".tiff"
    output_file_ending = ".png"
    image_name_ = image_name_without_ending
    input_path_ = "./raw_data/our_images/" + image_name_ + input_file_ending
    output_path_ = "./segmented_output_files/" + image_name_ + output_file_ending
    return input_path_, output_path_

def image_segmenter(source="local", clip=False): # destination="local"
    model = load_model('./model/model_ressources/unet-attention-3d.hdf5')
    if source=="local":
        input_path, output_path = path_constructor("after_resized")
        img = Image.open(input_path)
    # else: # plug in satellite input_api:

    if clip:
        img_array = np.array(img) / 255.0 * 3.5
        img_array = np.clip(a=img_array, a_min=0, a_max=1)
    else:
        img_array = np.array(img) / 255.0

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

    cropped_img.save(output_path)
    cropped_img_array = np.array(cropped_img, dtype=np.uint8)
    return cropped_img_array

# to be specified whereever this function will be used:
# model_ = load_model('./model/unet-attention-3d.hdf5')
# input_file_ending = ".tiff"
# output_file_ending = ".png"
# image_name_ = input("What is the name of the image file in the folder 'our_images' (without ending)? ")
# input_path_ = "./raw_data/our_images/" + image_name_ + input_file_ending
# output_path_ = "./segmented_output_files/" + image_name_ + output_file_ending
# image_segmenter(input_path_, output_path_, model_)
