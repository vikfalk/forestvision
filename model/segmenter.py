from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np

def image_segmenter(input_path, output_path, model):
    # open and scale image
    img = Image.open(input_path)
    img_array = np.array(img)/255.0

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

    # save the image
    cropped_img.save(output_path)
    print(f"\nSegmented image has successfully been saved at: \n{output_path}")

# model_ = load_model('./model/unet-attention-3d.hdf5')
# input_file_ending = ".tiff"
# output_file_ending = ".png"
# image_name_ = input("What is the name of the image file in the folder 'our_images' (without ending)? ")
# input_path_ = "./raw_data/our_images/" + image_name_ + input_file_ending
# output_path_ = "./segmented_output_files/" + image_name_ + output_file_ending
# image_segmenter(input_path_, output_path_, model_)
