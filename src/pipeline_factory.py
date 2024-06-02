from typing import Any

import dlt
from rest_api import (
    RESTAPIConfig,
    check_connection,
    rest_api_resources,
    rest_api_source,
)
from utils import read_secrets, read_sources


def run_pipeline(source_name: str, schema_name: str):
    sources = read_sources()
    source_config = sources["sources"][source_name]
    # secrets = read_secrets()
    source = rest_api_source(source_config)

    pipeline = dlt.pipeline(
        pipeline_name=f"{source_name}_pipeline",
        destination=dlt.destinations.duckdb("dlt_ingests.duckdb"),
        dataset_name=schema_name,
    )
    pipeline.run(source)


if __name__ == "__main__":
    run_pipeline("git", schema_name="raw")
