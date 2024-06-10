import streamlit as st
from utils import (
    SOURCES_PATH,
    get_source_names,
    read_source_config,
    run_pipeline,
)

# from pages.rest_api import ClientConfig, EndpointResource, RESTAPIConfig

st.set_page_config(page_title="Pipelines", page_icon="🚰")
st.title("Build Your `dlt` Pipeline")


def configure_source():
    st.markdown("### Source")
    source_names = get_source_names()
    source_name = st.selectbox("Choose an existing source", options=source_names)
    return source_name


def configure_destination():
    st.markdown("### Destination")
    left, right = st.columns(2)
    with left:
        destination_name = st.selectbox(
            "Choose a destination",
            options=[
                "DuckDB",
                "Snowflake",
            ],
        )
    with right:
        schema = st.text_input("Schema name")
    return destination_name, schema
    # left, center, right = st.columns([0.49, 0.02, 0.49])
    # with left:
    #     database = st.text_input("Database")
    # with center:
    #     st.text("")
    #     st.text("")
    #     st.text("")
    #     st.markdown(".")
    # with right:


source_name = configure_source()
if source_name:
    destination_name, schema_name = configure_destination()
    if schema_name != "":
        st.markdown("### Pipeline Results")
        if st.button("Run Pipeline"):
            load_info = run_pipeline(source_name=source_name, schema_name=schema_name)
            st.success(load_info)
