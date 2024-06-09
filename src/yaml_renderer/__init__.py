from distutils.dir_util import copy_tree
from pathlib import Path

from dlt_init_openapi.config import REST_API_SOURCE_LOCATION, Config
from dlt_init_openapi.parser.openapi_parser import OpenapiParser
from dlt_init_openapi.renderer.base_renderer import BaseRenderer
from dlt_init_openapi.utils import misc
from jinja2 import Environment, PackageLoader
from utils import SOURCES_PATH

FILE_ENCODING = "utf-8"
TEMPLATE_FILTERS = {
    "snakecase": misc.snake_case,
    "kebabcase": misc.kebab_case,
    "pascalcase": misc.pascal_case,
    "any": any,
}
# SOURCES_PATH = Path(__file__).parents[2] / "sources"


class YAMLRenderer(BaseRenderer):
    openapi: OpenapiParser

    def __init__(self, config: Config) -> None:
        self.config = config

        self.env: Environment = Environment(
            loader=PackageLoader(__package__),
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=["jinja2.ext.loopcontrols"],
            keep_trailing_newline=True,
        )

        self.env.filters.update(TEMPLATE_FILTERS)

    def run(self, openapi: OpenapiParser, dry: bool = False) -> None:
        """Run the renderer"""
        self.openapi = openapi

        # set up some paths
        self.package_name = (
            self.config.package_name or self.config.project_name
        ).replace("-", "_")
        self.source_name = self.package_name + "_source"
        self.dataset_name = self.package_name + self.config.dataset_name_suffix
        self.package_dir = self.config.project_dir / self.package_name

        self.env.globals.update(
            utils=misc,
            class_name=lambda x: misc.ClassName(x, ""),
            package_name=self.package_name,
            project_name=self.config.project_name,
            credentials=self.openapi.detected_global_security_scheme,
            config=self.config,
        )

        if dry:
            return

        self._build_source()

    def _build_source(self) -> None:
        module_path = SOURCES_PATH / f"{self.package_name}.yaml"
        module_path.write_text(
            self._render_source(),
            encoding=FILE_ENCODING,
        )

    def _render_source(self) -> str:
        template = self.env.get_template("source.yaml.j2")
        return template.render(
            base_url=self.openapi.info.servers[0].url,
            other_servers=self.openapi.info.servers[1:],
            source_name=self.source_name,
            endpoint_collection=self.openapi.endpoints,
            imports=[],
            global_paginator_config=(
                self.openapi.detected_global_pagination.paginator_config
                if self.openapi.detected_global_pagination
                else None
            ),
        )
