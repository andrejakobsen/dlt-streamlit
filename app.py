import streamlit as st

from sub_pages.page_1 import Page1
from sub_pages.page_2 import Page2
from sub_pages.source_builder import PageMain
from utils.utils import app_base_config


def layout():
    st.sidebar.title("dlt Streamlit")
    st.sidebar.header("Menu")

    page_name = st.sidebar.selectbox(
        "Please select a page",
        ["Connector Builder", "Page 1", "Page 2"],
    )

    page_wrapper: dict = {
        "Connector Builder": PageMain(),
        "Page 1": Page1(),
        "Page 2": Page2(),
    }

    page = page_wrapper[page_name]
    page.display_page()


if __name__ == "__main__":
    app_base_config()
    layout()
