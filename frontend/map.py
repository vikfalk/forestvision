import pydeck as pdk
import streamlit as st


SQUARE_SIDE_LENGTH = 5.12
EQUATOR_LATITUDINAL_DEGREE_IN_KM = 110.6
EQUATOR_LONGITUDINAL_DEGREE_IN_KM = 111.3
MEAN_GCS_DEGREE = (EQUATOR_LATITUDINAL_DEGREE_IN_KM + EQUATOR_LONGITUDINAL_DEGREE_IN_KM) / 2


def create_polygon_layer(lng, lat):
    half_side_length = SQUARE_SIDE_LENGTH / 2 / MEAN_GCS_DEGREE
    lng, lat = float(lng), float(lat)
    square_coords = [
        [lng - half_side_length, lat - half_side_length],
        [lng + half_side_length, lat - half_side_length],
        [lng + half_side_length, lat + half_side_length],
        [lng - half_side_length, lat + half_side_length],
        [lng - half_side_length, lat - half_side_length]
    ]

    polygon_data = [{
        "polygon": square_coords,
        "name": "Deforestation Area"
    }]

    polygon_layer = pdk.Layer(
        'PolygonLayer',
        data=polygon_data,
        get_polygon='polygon',
        get_fill_color=[153, 70, 54, 40],
        get_line_color=[153, 70, 54, 100],
        get_line_width=10,
        pickable=True,
        extruded=False
    )
    return polygon_layer


def inject_map(lng, lat, zoom):
    view_state = pdk.ViewState(
        longitude=float(lng),
        latitude=float(lat),
        zoom=zoom
    )
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/satellite-streets-v12',
        initial_view_state=view_state,
        layers=[create_polygon_layer(lng, lat)],
        tooltip=False
    ))
