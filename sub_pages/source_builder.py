import streamlit as st

from ._page_base import BasePageLayout
from .rest_api import ClientConfig, EndpointResource, RESTAPIConfig


# client: ClientConfig
# resource_defaults: Optional[EndpointResourceBase]
# resources: List[Union[str, EndpointResource]]
class PageMain(BasePageLayout):
    def __init__(self):
        super().__init__()

    def page_content(self):
        st.title("Build Your `dlt` Pipeline")
        st.markdown("* * *")
        with st.expander("Client", expanded=True):
            client_config = self.get_client_config()
        with st.expander("Endpoints", expanded=True):
            if st.checkbox(
                "Default configuration",
                help=(
                    "Applied to all endpoints unless overridden by the endpiont's specific configuration."
                ),
            ):
                resource_defaults_config = self.get_resource_defaults()
            st.markdown("### Endpoints")
            n_resources = st.number_input(
                "Number of endpoints", min_value=1, max_value=50
            )
        config: RESTAPIConfig = {"client": client_config}

    def get_client_config(self):
        client_config = {
            "base_url": st.text_input(
                "Base URL", placeholder="https://api.example.com/v1"
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
        client_config["auth"] = self._get_auth_input(auth_type)

        return client_config

    def get_resource_defaults(self):
        st.markdown("#### Defaults")
        resource_defaults_config = {}
        col_1, col_2 = st.columns(2)
        with col_1:
            resource_defaults_config["write_disposition"] = st.radio(
                "Write disposition", ("merge", "replace", "append"), horizontal=True
            )
        with col_2:
            resource_defaults_config["primary_key"] = st.text_input(
                "Primary key", placeholder="id"
            )
        resource_defaults_config["endpoint"] = {"params": {}}

    def _get_auth_input(self, auth_type):
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
