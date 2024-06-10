import pathlib
import sys
from typing import Any, Optional

import questionary
from dlt_init_openapi.cli import _load_config
from dlt_init_openapi.cli.cli_endpoint_selection import questionary_endpoint_selection
from dlt_init_openapi.exceptions import DltOpenAPITerminalException
from dlt_init_openapi.utils import update_rest_api
from loguru import logger


def create_pipeline(
    source: str,
    url: Optional[str] = None,
    path: Optional[pathlib.Path] = None,
    output_path: Optional[pathlib.Path] = None,
    config_path: Optional[pathlib.Path] = None,
    interactive: bool = False,
    log_level: int = 20,
    global_limit: int = 0,
    update_rest_api_source: bool = False,
    allow_openapi_2: bool = True,
) -> None:
    """Adapted from `_init_command_wrapped` function
    in the `dlt-init-openapi` library"""
    from dlt_init_openapi import create_new_client

    # set up console logging
    logger.remove()
    logger.add(sys.stdout, level=log_level)
    logger.success("Starting dlt openapi generator")

    try:
        # sync rest api
        update_rest_api.update_rest_api(force=update_rest_api_source)

        config = _load_config(
            path=config_path,
            config={
                "project_name": source,
                "package_name": source,
                "output_path": output_path,
                "endpoint_filter": questionary_endpoint_selection
                if interactive
                else None,
                "global_limit": global_limit,
                "spec_url": url,
                "spec_path": path,
                "allow_openapi_2": allow_openapi_2,
                "renderer_class": "yaml_renderer.YAMLRenderer",
            },
        )

        if config.project_dir.exists():
            if not interactive:
                logger.info(
                    "Non interactive mode selected, overwriting existing source."
                )
            elif not questionary.confirm(
                f"Directory {config.project_dir} exists, do you want to continue and update the generated files? "
                + "This will overwrite your changes in those files."
            ).ask():
                logger.warning("Exiting...")
                exit(0)

        create_new_client(
            config=config,
        )
        logger.success(
            "Pipeline created. Learn more at https://dlthub.com/docs. See you next time :)"
        )

    except DltOpenAPITerminalException as exc:
        logger.error("Encountered terminal exception:")
        logger.error(exc)
        logger.info("Exiting...")


if __name__ == "__main__":
    create_pipeline(
        source="nav",
        url="https://data.brreg.no/enhetsregisteret/api/v3/api-docs",
        interactive=False,
        global_limit=20,
        allow_openapi_2=True,
    )
