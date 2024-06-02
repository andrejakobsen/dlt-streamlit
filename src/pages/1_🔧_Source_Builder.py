import json

import streamlit as st
from utils import (
    SOURCES_PATH,
    read_secrets,
    read_sources,
    write_sources,
)

# from pages.rest_api import ClientConfig, EndpointResource, RESTAPIConfig

st.set_page_config(page_title="Build REST API Source", page_icon="🔧")
st.title("Build a REST API Source")


def source_builder(name: str):
    # st.markdown(f"## Creating '{name}' Source")
    st.markdown(f"#### 1. Configure the base client for '{name}'")
    with st.expander("Client", expanded=True):
        client_config = get_client_config()
    if client_config["base_url"] != "":
        st.markdown(f"#### 2. Choose default configuration for '{name}'")
        with st.expander("Default Configuration"):
            resource_defaults_config = get_resource_standard_config()
        # st.json(params)
        st.markdown(f"#### 3. Configure the endpoints for '{name}'")
        with st.expander("Endpoints"):
            n_resources = st.number_input(
                "Number of endpoints", min_value=1, max_value=50
            )
            resources_config = []

            for i in range(int(n_resources)):
                st.divider()
                resources_config.append(get_resources_config(i))
        if resources_config[0]:
            source_config = {
                "client": client_config,
                "resource_defaults": resource_defaults_config,
                "resources": resources_config,
            }
            st.markdown(
                f"#### 4. Make sure the conifguration for '{name}' looks as expected"
            )
            st.json(source_config)
            return source_config


def get_client_config():
    client_config = {
        "base_url": st.text_input(
            "Base URL", placeholder="https://api.github.com/repos/dlt-hub/dlt/"
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
    )
    auth = _get_auth_input(auth_type)
    if auth is not None:
        client_config["auth"] = auth  # type: ignore

    return client_config


def get_resource_standard_config(name: str = "Default"):
    resource_defaults_config = {}
    col_1, col_2 = st.columns(2)
    with col_1:
        resource_defaults_config["write_disposition"] = st.radio(
            f"Write disposition for '{name}'",
            ("replace", "merge", "append"),
            horizontal=True,
        )
    with col_2:
        resource_defaults_config["primary_key"] = st.text_input(
            f"Primary key for '{name}'", placeholder="id"
        )
    left, right = st.columns(2)
    params = {}
    params_type = "JSON"
    with left:
        use_params = st.checkbox("Use parameters", key=f"checkbox_{name}")
    with right:
        if use_params:
            params_type = st.radio(
                "Choose",
                ("Key/value", "JSON"),
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
                        value='{\n  "": ""\n}',
                        key=f"json_text_{name}",
                    )
                )
            else:
                n_params = st.number_input(
                    "Number of parameters",
                    min_value=1,
                    max_value=50,
                    key=f"number_{name}",
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
        resource_defaults_config["endpoint"] = {"params": params}
    return resource_defaults_config


def get_resources_config(endpoint_idx):
    resource_config = {}
    left, right = st.columns(2)
    with left:
        endpoint = st.text_input(f"Endpoint {endpoint_idx+1}", placeholder="issues")
    if endpoint != "":
        with right:
            name = st.text_input(f"Name for '{endpoint}'", value=endpoint)
            resource_config["name"] = name
        if endpoint != "":
            use_custom_params = st.checkbox(
                f"Use custom configuration for '{name}'",
            )
            if use_custom_params:
                resource_config |= get_resource_standard_config(name)
        if "endpoint" not in resource_config.keys():
            resource_config["endpoint"] = {}
        resource_config["endpoint"]["path"] = endpoint

    return resource_config


def _get_auth_input(auth_type):
    if auth_type == "Bearer Token":
        return {
            "token": st.text_input("Token", type="password"),
        }
    elif auth_type == "API Key":
        return {
            "name": st.text_input("Username"),
            "password": st.text_input("Password", type="password"),
            "location": st.selectbox("Location", ("header", "query")),
        }
    elif auth_type == "HTTP Basic Authentication":
        return {
            "username": st.text_input("Username"),
            "password": st.text_input("Password", type="password"),
        }
    else:
        return {}


source_name = st.text_input("Name of new source", placeholder="GitHub")
if source_name != "":
    # create_source = st.button("Create Source")
    source_config = source_builder(source_name)
    if st.button("Save source"):
        sources = read_sources()
        sources["sources"][source_name] = source_config
        write_sources(sources)
