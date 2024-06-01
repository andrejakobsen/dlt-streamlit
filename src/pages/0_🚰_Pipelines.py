import streamlit as st

# from pages.rest_api import ClientConfig, EndpointResource, RESTAPIConfig

st.set_page_config(page_title="Pipelines", page_icon="🚰")
st.title("Build Your `dlt` Pipeline")

source_tab, destination_tab, run_pipeline = st.tabs(
    ["Source", "Destination", "Run Pipeline"]
)

with source_tab:
    source_name = st.selectbox(
        "Choose an existing source", options=["Salesforce", "GitHub"]
    )
    st.text_input("Name")

with destination_tab:
    source_name = st.selectbox("Choose a destination", options=["Snowflake", "DuckDB"])
    left, center, right = st.columns([0.49, 0.02, 0.49])
    with left:
        database = st.text_input("Database")
    with center:
        st.text("")
        st.text("")
        st.text("")
        st.markdown(".")
    with right:
        schema = st.text_input("Schema")
with run_pipeline:
    st.button("Run")
