from PIL import Image
import numpy as np

def calculate_black_coverage(image_array):
    total_pixels = image_array.size
    black_pixels = np.sum(image_array == 0)
    return black_pixels / total_pixels * 100

def compare_coverage(
    image_1_path="./segmented_output_files/generic_test.png",
    image_2_path="./segmented_output_files/without_clouds.png"
    ):

    image_1 = Image.open(image_1_path)
    image_2 = Image.open(image_2_path)

    array_1 = np.array(image_1)
    array_2 = np.array(image_2)

    forest_coverage_1 = calculate_black_coverage(array_1)
    forest_coverage_2 = calculate_black_coverage(array_2)
    change_phrase = "an increase" if forest_coverage_1 < forest_coverage_2 else "a decrease"
    change_percentage = round(((forest_coverage_2 - forest_coverage_1) / forest_coverage_1) * 100, 2)

    result_string = (f"""
    The forest coverage on the first image is {round(forest_coverage_1, 2)} %,
    the forest coverage on the second image is {round(forest_coverage_2, 2)} %.
    That is {change_phrase} of {change_percentage} %.
    """)
    return result_string
