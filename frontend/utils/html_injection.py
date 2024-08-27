import streamlit as st
from utils.metrics_processing import convert_to_ha


DARK_BLUE = "#262730"
LIGHT_RED = "#994636"


def inject_bold_centered(text: str, font_em: float=1):
    st.markdown(
        f"""<p style='text-align: center; font-weight: bold; font-size: {font_em}em'> {text}</p>""",
        unsafe_allow_html=True
    )


def inject_metric_bar(text: str, metric: float, unit: str = '%'):
    st.markdown(
        f"""
        {text}
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: {DARK_BLUE};
            border-radius: 10px;
            padding: 5px;
            height: 3em;
            width: {metric if metric > 25 else 25}%;
            position: relative;">
            <p style="
                font-weight: bold;
                font-size: 1.25em;
                margin: 0;
                width: 100%;
            ">
                {metric if unit == '%' else convert_to_ha(metric):.0f}{unit}
            </p>
        </div>""",
        unsafe_allow_html=True
    )


def inject_total_change(metric: float, unit: str):
    st.markdown(
        f"""
        Total Change
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: {LIGHT_RED};
            border-radius: 10px;
            padding: 5px;
            height: 6em;
        ">
            <p style="
                font-weight: bold;
                font-size: 2.5em;
                margin: 0;
            ">
                {metric:.0f}{unit}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown('')
