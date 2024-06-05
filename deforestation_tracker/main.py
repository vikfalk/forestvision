import os
from tensorflow.keras.models import load_model
import os
import numpy as np
import datetime as dt
from PIL import Image
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from deforestation_tracker.segmenter import segment, segment_self
from deforestation_tracker.image_array_loaders import load_img_array_from_satellite, load_img_array_locally, load_multiple_imgs_from_sat
from deforestation_tracker.custom_layer import RepeatElements

# INSTRUCTION:
# Run this file, triggering the __main__ function.
# Go to "http://localhost:8080/docs" to test it out.

app = FastAPI()

@app.get('/')
def index():
    return {'api status': "running"}

@app.get("/get_image_from_satellite_with_params")
def get_image_from_satellite_with_params(
    start_timeframe: str,
    end_timeframe: str,
    longitude: str,
    latitude: str,
    sample_number: str,
    square_size: str):

    model = load_model('./deforestation_tracker/model_ressources/unet-attention-3d.hdf5')
    image_array, request_info_date = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(end_timeframe),  # assuming format "2023-02-03"
    )

    original_image_list = image_array.flatten().tolist()

    image_array = segment(image_array, model)
    image_list = image_array.tolist()
    return JSONResponse(content={"original_image_list": original_image_list,
                                 "segmented_image_list": image_list,
                                 "request_info_date": request_info_date})

@app.get("/do_everything")
def do_everything(
    start_timeframe: str,  # TODO: Pay attention to unused inputs.
    end_timeframe: str,
    longitude: str,
    latitude: str,
    sample_number: str,  # TODO: Pay attention to unused inputs.
    square_size: str):  # TODO: Pay attention to unused inputs.

    model = load_model('./deforestation_tracker/model_ressources/unet-attention-3d.hdf5')

    #End sat pull
    end_sat_image_array, end_date_info = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(end_timeframe)  # assuming format "2023-02-03"
    )

    start_sat_image_array, start_date_info = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(start_timeframe)  # assuming format "2023-02-03"
    )

    #End sat present
    end_sat_image_list = end_sat_image_array.tolist()

    #End mask present
    end_mask_image_array = segment(end_sat_image_list, model)
    end_mask_image_list = end_mask_image_array.tolist()

    #Start sat present
    start_sat_image_list = start_sat_image_array.tolist()

    #Start mask present
    start_mask_image_array = segment(start_sat_image_list, model)
    start_mask_image_list = start_mask_image_array.tolist()

    return JSONResponse(content={"end_mask_image_list": end_mask_image_list,
                                 "end_sat_image_list": end_sat_image_list,
                                 "start_mask_image_list": start_mask_image_list,
                                 "start_sat_image_list": start_sat_image_list,
                                 'start_date_info':start_date_info,
                                 'end_date_info': end_date_info,
                                 })

# Selfmade model endpoints

@app.get("/get_image_from_satellite_self")
def get_image_from_satellite_self():
    model = load_model('./deforestation_tracker/model_ressources/att_unet_4b.hdf5', custom_objects={'RepeatElements': RepeatElements})
    image_array, request_info_date = load_img_array_from_satellite(request_type='4-band')
    # Scale image array to have the same scale as training images that have been
    # preprocessed with rasterio
    max_values = np.max(image_array, axis=(0, 1))
    image_array = image_array / max_values
    # Retain the original satellite image and convert it to 3-band
    original_image_array = image_array
    original_image_array = original_image_array[:,:,:3]
    original_image_list = original_image_array.flatten().tolist()
    # Segment the 4-band version of the satellite image
    image_array = segment_self(image_array, model)
    image_list = image_array.flatten().tolist()
    return JSONResponse(content={"original_image_list": original_image_list,
                                "segmented_image_list": image_list,
                                "request_info_date": request_info_date})

@app.get("/get_image_from_satellite_with_params_self")
def get_image_from_satellite_with_params_self(
    start_timeframe: str,  # TODO: Pay attention to unused inputs.
    end_timeframe: str,
    longitude: str,
    latitude: str,
    sample_number: str,  # TODO: Pay attention to unused inputs.
    square_size: str):  # TODO: Pay attention to unused inputs.
    image_list = float(latitude), float(longitude), end_timeframe
    model = load_model('./deforestation_tracker/model_ressources/att_unet_4b.hdf5', custom_objects={'RepeatElements': RepeatElements})
    image_array, request_info_date = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(end_timeframe),  # assuming format "2023-02-03"
        request_type='4-band'
    )

    # Scale image array to have the same scale as training images that have been
    # preprocessed with rasterio
    max_values = np.max(image_array, axis=(0, 1))
    image_array = image_array / max_values
    # Retain the original satellite image and convert it to 3-band
    original_image_array = image_array
    original_image_array = original_image_array[:,:,:3]
    original_image_list = original_image_array.flatten().tolist()
    # Segment the 4-band version of the satellite image
    image_array = segment_self(image_array, model)
    image_list = image_array.flatten().tolist()
    return JSONResponse(content={"original_image_list": original_image_list,
                                "segmented_image_list": image_list,
                                "request_info_date": request_info_date})

# @app.get("/get_multiple_images_from_satellite")
# def get_multiple_images_from_satellite(
#     start_timeframe: str,  # TODO: Pay attention to unused inputs.
#     end_timeframe: str,
#     longitude: str,
#     latitude: str,
#     sample_number: str):  # TODO: Pay attention to unused inputs.
#     # construct list with request dates
#     start_dt, end_dt = dt.datetime.strptime(start_timeframe, "%Y-%m-%d"), dt.datetime.strptime(end_timeframe, "%Y-%m-%d")
#     date_step_size = (end_dt - start_dt)/(sample_number - 1)
#     date_list = [dt.date.strftime(start_dt + i * date_step_size, "%Y-%m-%d") for i in range(sample_number)]
#     date_list_loaded, img_list = load_multiple_imgs_from_sat(lat_deg=latitude, lon_deg=longitude, date_list=date_list, request_type='TrueColor')
#     test_img = img_list[0]
#     test_img_list = test_img.flatten().tolist()
#     return JSONResponse(content={"test_img_list": test_img_list
#                                 })

# DAVIDS REWORKED VERSION
@app.get("/get_multiple_images_from_satellite")
def get_multiple_images_from_satellite(
        start_timeframe: str = "2020-05-13",
        end_timeframe: str = "2024-05-30",
        longitude: str = "-55.26209",  # TODO: Check if incoming data is really of type string
        latitude: str = "-8.48638",  # TODO: Check if incoming data is really of type string
        sample_number: str = "2"):  # TODO: Check if incoming data is really of type string

        model = load_model('./deforestation_tracker/model_ressources/att_unet_4b.hdf5', custom_objects={'RepeatElements': RepeatElements})

        # construct list with request dates
        start_dt, end_dt = dt.datetime.strptime(start_timeframe, "%Y-%m-%d"), dt.datetime.strptime(end_timeframe, "%Y-%m-%d")
        date_step_size = (end_dt - start_dt)/(int(sample_number) - 1)
        date_list = [dt.date.strftime(start_dt + i * date_step_size, "%Y-%m-%d") for i in range(int(sample_number))]
        # load both 3 band and 4 band images
        date_list_loaded, img_list = load_multiple_imgs_from_sat(lat_deg=float(latitude), lon_deg=float(longitude), date_list=date_list, request_type='TrueColor')

        # Join 3-band with 4-band
        number_of_dates = len(date_list_loaded)
        combined_img_arrays = []
        for date in range(number_of_dates):
            band_4_at_date = img_list[(date + number_of_dates)][:,:,3]#(datefour_b_array_end[:,:,3]
            vis_at_date = img_list[date]
            # Normalize 4-band channel to values between 0 and 1
            max_value = np.max(band_4_at_date)
            band_4_at_date = band_4_at_date / max_value
            combined_img_arrays.append(np.dstack((vis_at_date, band_4_at_date)))
        print(f'No of combined 4-band arrays: {len(combined_img_arrays)}')
        print(f'Shape of 4-band arrays: {combined_img_arrays[0].shape}')
        # Segment
        # Create segmentation masks
        # for i in combined_img_arrays:
        #     print(i.shape)

        segmented_arrays = [segment(img_at_date, model) for img_at_date in combined_img_arrays]
        print(f'Shape of segmented arrays: {segmented_arrays[0].shape}')
        # processing of image arrays
        original_img_list = [img.flatten().tolist() for img in combined_img_arrays]
        original_img_list_flat = [x for img in original_img_list for x in img]
        segmented_img_list = [mask.flatten().tolist() for mask in segmented_arrays]
        segmented_img_list_flat = [x for mask in segmented_img_list for x in mask]
         return JSONResponse(content = {"date_list_loaded": date_list_loaded, "original_img_list": original_img_list_flat,
                   "segmented_img_list": segmented_img_list_flat})
        # # TEST CODE
        # content = {"date_list_loaded": date_list_loaded, "original_img_list": original_img_list_flat,
        #            "segmented_img_list": segmented_img_list_flat}
        # return content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ["PORT"]))
    # # TEST CODE
    # content_ = get_multiple_images_from_satellite(sample_number=2)
    # [print(date) for date in content_.get("date_list_loaded")]
    # print(f'Length of original img list : {len(content_.get("original_img_list"))}')
    # print(f'Length of segmented img list : {len(content_.get("segmented_img_list"))}')

    #[print(img) for img in content_.get("original_img_list")]
    #[print(img[:1]) for img in content_.get("segmented_img_list")]
