import os
import io
import base64
import datetime as dt
import numpy as np
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model
from backend.custom_layer import RepeatElements
from backend.segmenter import segment
from backend.image_array_loader import load_multiple_imgs_from_sat

def numpy_to_base64(img_array):
    img_bytes = io.BytesIO()
    np.save(img_bytes, img_array)
    img_bytes.seek(0)
    img_b64 = base64.b64encode(img_bytes.read()).decode('utf-8')
    return img_b64

app = FastAPI()

@app.get('/')
def index():
    return {'api status': "running"}

@app.get("/get_satellite_images")
def get_satellite_images(
    start_timeframe: str = "2020-05-13",
    end_timeframe: str = "2024-05-30",
    longitude: str = "-55.26209",
    latitude: str = "-8.48638",
    sample_number: str = "2",
    send_orginal_images = 'False'
    ):
    """Takes start and end date and coordinates and returns
    a JSON response object including dates, segmented images and optionally,
    original images. If sample_number equals two, only data belonging to the
    closest point in time to the start and the end date respectively will be
    returned, higher sample_numbers will return data from points in time between
    the start and the end date, as evenly spaced as possible.
    """

    # Construct list with request dates
    start_dt = dt.datetime.strptime(start_timeframe, "%Y-%m-%d")
    end_dt = dt.datetime.strptime(end_timeframe, "%Y-%m-%d")
    date_step_size = (end_dt - start_dt)/(int(sample_number) - 1)
    date_list = [
        dt.date.strftime(start_dt + i * date_step_size, "%Y-%m-%d")
        for i in range(int(sample_number))
    ]

    # Load both 3-band and 4-band images
    loaded_dates, img_arrays = load_multiple_imgs_from_sat(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        date_list=date_list
    )

    # Join 3- with 4-band, normalize 4-band channel to values between 0 and 1
    number_of_dates = len(loaded_dates)
    original_img_arrays = []
    combined_img_arrays = []
    for date in range(number_of_dates):
        band_4_at_date = img_arrays[(date + number_of_dates)][:,:,3]
        vis_at_date = img_arrays[date]
        rescaled_vis_at_date = (vis_at_date * 255).astype(np.uint8)
        original_img_arrays.append(rescaled_vis_at_date)
        max_value = np.max(band_4_at_date)
        band_4_at_date = band_4_at_date / max_value
        combined_img_arrays.append(np.dstack((vis_at_date, band_4_at_date)))

    # Segmenting
    model = load_model(
        filepath='./backend/model_ressources/att_unet_4b.hdf5',
        custom_objects={'RepeatElements': RepeatElements}
    )
    segmented_img_arrays = [
        segment(img_at_date, model, threshold=0.7)
        for img_at_date in combined_img_arrays
    ]

    # Removing entries that corresponed to misshaped segmented_img_array
    for i, arr in enumerate(segmented_img_arrays):
        if arr.shape != (512, 512):
            loaded_dates.pop(i)
            original_img_arrays.pop(i)
            segmented_img_arrays.pop(i)

    # Encoding
    segmented_img_b64_list = [
        numpy_to_base64(img)
        for img in segmented_img_arrays
    ]
    original_img_b64_list = [
        numpy_to_base64(img)
        for img in original_img_arrays
    ]

    # Transmitting
    if send_orginal_images == 'False':
        print("Not sending original satellite images.")
        json_response_content = {
                "date_list_loaded": loaded_dates,
                "segmented_img_list": segmented_img_b64_list}
    elif send_orginal_images == 'True':
        print(
            "Sending original satellite images,",
            "too under the key 'original_img_list'."
        )
        json_response_content = {
                "date_list_loaded": loaded_dates,
                "segmented_img_list": segmented_img_b64_list,
                "original_img_list": original_img_b64_list}
    return JSONResponse(content=json_response_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ["PORT"]))
