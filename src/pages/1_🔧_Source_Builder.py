import json

import streamlit as st
from dlt import resource
from questionary import autocomplete
from rest_api import RESTAPIConfig
from rest_api.typing import ClientConfig
from source_factory import create_pipeline
from utils import (
    SOURCES_PATH,
    get_source_names,
    get_source_path,
    read_source_config,
    write_source,
)

# from pages.rest_api import ClientConfig, EndpointResource, RESTAPIConfig

st.set_page_config(page_title="Build REST API Source", page_icon="🔧")
st.title("Build a REST API Source")


def source_builder(name: str, source_config: RESTAPIConfig, key: int):
    # st.markdown(f"## Creating '{name}' Source")
    st.markdown(f"#### 1. Configure the base client for '{name}'")
    with st.expander("Client"):
        source_config["client"] = get_client_config(source_config["client"], key)
    st.markdown(f"#### 2. Choose default configuration for '{name}'")
    with st.expander("Default Configuration"):
        source_config["resource_defaults"] = get_resource_standard_config(
            source_config.get("resource_defaults", {}), key=key
        )
    # st.json(params)
    st.markdown(f"#### 3. Configure the endpoints for '{name}'")
    with st.expander("Endpoints"):
        n_resources = st.number_input(
            "Number of endpoints",
            value=len(source_config.get("resources", [])),
            min_value=1,
            max_value=100,
            key=f"{name}_{key}",
        )
        resources_config = []

        for i in range(int(n_resources)):
            st.divider()
            resources_config.append(
                get_resources_config(source_config.get("resources", []), i, key)
            )
    if resources_config[0]:
        st.markdown(
            f"#### 4. Make sure the conifguration for '{name}' looks as expected"
        )
        st.json(source_config)
        return source_config


def get_client_config(client_config, key: int) -> ClientConfig:
    client_config = {
        "base_url": st.text_input(
            "Base URL",
            value=client_config.get("base_url", ""),
            placeholder="https://api.github.com/repos/dlt-hub/dlt/",
            key=f"base_url_{key}",
        ),
    }
    auth_type = st.selectbox(
        "Authentication",
        (
            "None",
            "Bearer Token",
            "API Key",
            "HTTP Basic Authentication",
        ),
        key=f"auth_{key}",
    )
    auth = _get_auth_input(auth_type, key)
    if auth:
        client_config["auth"] = auth  # type: ignore

    return client_config


def get_resource_standard_config(resource_config, key: int, name: str = "Default"):
    col_1, col_2 = st.columns(2)
    with col_1:
        primary_key = st.text_input(
            f"Primary key for '{name}'",
            value=resource_config.get("primary_key", ""),
            placeholder="id",
            key=f"{name}_{key}",
        )
        if primary_key:
            resource_config["primary_key"] = primary_key
    with col_2:
        resource_config["write_disposition"] = st.radio(
            label=f"Write disposition for '{name}'",
            index=1 if primary_key else 0,
            options=("replace", "merge", "append"),
            horizontal=True,
            key=f"write_disposition_{name}_{key}",
        )
    left, right = st.columns(2)
    params = {}
    params_type = "JSON"
    with left:
        use_params = st.checkbox(
            "Use parameters",
            key=f"checkbox_{name}_{key}",
            value=True if resource_config.get("params", "") else False,
        )
    with right:
        if use_params:
            params_type = st.radio(
                "Choose",
                ("JSON", "Key/value"),
                horizontal=True,
                label_visibility="collapsed",
                key=f"radio_resource_{name}",
            )

    if use_params:
        with right:
            if params_type == "JSON":
                params = json.loads(
                    st.text_area(
                        "Parameters in JSON format",
                        value=resource_config.get("params", '{\n  "": ""\n}'),
                        key=f"json_text_{name}",
                    )
                )
            else:
                n_params = st.number_input(
                    "Number of parameters",
                    min_value=1,
                    max_value=50,
                    key=f"number_{name}_{key}",
                )
                left_inner, right_inner = st.columns(2)

                for i in range(int(n_params)):
                    with left_inner:
                        key = st.text_input(
                            f"Key {i+1}", placeholder="limit", key=f"key_{i}_{name}"
                        )
                    with right_inner:
                        value = st.text_input(
                            f"Value {i+1}", placeholder="50", key=f"value_{i}_{name}"
                        )
                        try:
                            value = int(value)
                        except ValueError:
                            pass
                        if value == "true":
                            value = True
                        elif value == "false":
                            value = False
                    params[key] = value
        with left:
            st.markdown("Resulting parameters")
            st.json(params)
        resource_config["endpoint"] = {"params": params}
    return resource_config


def get_resources_config(resource_config, endpoint_idx, key: int):
    current_resource = resource_config[endpoint_idx]
    left, right = st.columns(2)
    with left:
        endpoint_config = current_resource.get("endpoint", {})
        endpoint = st.text_input(
            f"Endpoint {endpoint_idx+1}",
            value=endpoint_config.get("path", ""),
            placeholder="issues",
            key=f"{endpoint_idx}_{key}",
        )
    if endpoint != "":
        with right:
            table_name = st.text_input(
                f"Table name for '{endpoint}'",
                value=current_resource.get("table_name", ""),
            )
            resource_config[endpoint_idx]["table_name"] = table_name
        if endpoint != "":
            use_custom_params = st.checkbox(
                f"Use custom configuration for '{table_name}'",
            )
            if use_custom_params:
                resource_config |= get_resource_standard_config(
                    resource_config, key=key + endpoint_idx, name=table_name
                )

        if "endpoint" not in resource_config.keys():
            resource_config["endpoint"] = {}
        resource_config["data_selector"] = st.text_input(
            f"Data selector for '{endpoint}'",
            value=resource_config.get("data_selector", ""),
        )
        resource_config["endpoint"]["path"] = endpoint

    return resource_config


def _get_auth_input(auth_type, key: int):
    if auth_type == "Bearer Token":
        return {
            "token": st.text_input("Token", type="password", key=f"token_{key}"),
        }
    elif auth_type == "API Key":
        return {
            "name": st.text_input("Username", key=f"username_{key}"),
            "password": st.text_input(
                "Password", type="password", key=f"password_{key}"
            ),
            "location": st.selectbox("Location", ("header", "query"), key=f"loc_{key}"),
        }
    elif auth_type == "HTTP Basic Authentication":
        return {
            "username": st.text_input("Username", key=f"username_2_{key}"),
            "password": st.text_input(
                "Password", type="password", key=f"password_2_{key}"
            ),
        }
    else:
        return {}


def openapi_source_builder(source_name):
    st.markdown(
        f"#### 0. Use `dlt_init_openapi` to generate source for '{source_name}'"
    )
    openapi_docs_url = st.text_input("OpenAPI Docs URL")
    if st.button("Generate source"):
        create_pipeline(source_name, url=openapi_docs_url)
        return read_source_config(get_source_path(source_name))


edit_source_tab, create_source_tab = st.tabs(["Edit Source", "Create Source"])
with edit_source_tab:
    existing_sources = get_source_names()
    if existing_sources:
        source_name = st.selectbox("Choose an existing source", existing_sources)
        source_config = read_source_config(source_name)
        source_config = source_builder(source_name, source_config, key=0)
    else:
        st.info("No sources found. You can create a new source instead.")
with create_source_tab:
    source_name = st.text_input("Name of new source", placeholder="GitHub")
    source_path = get_source_path(source_name)
    if source_path.exists():
        st.error(f"The source '{source_name}' already exists.")
    elif source_name != "":
        source_config = openapi_source_builder(source_name)
        st.markdown(source_config)
        source_config = read_source_config(source_name)
        source_config = source_builder(source_name, source_config, key=1)
        if st.button("Save source"):
            sources = read_source_config(source_name)
            write_source(sources)
