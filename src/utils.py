from pathlib import Path

import dlt
import yaml
from rest_api import RESTAPIConfig, rest_api_source
from rest_api.typing import ClientConfig, EndpointResourceBase

ROOT_DIR = Path(__file__).parents[1]
SOURCES_PATH = ROOT_DIR / "sources"


def run_pipeline(source_name: str, schema_name: str):
    source_config = read_source_config(source_name)
    source = rest_api_source(source_config)
    source.add_limit(1000)

    pipeline = dlt.pipeline(
        pipeline_name=f"{source_name}_pipeline",
        destination=dlt.destinations.duckdb("dlt_ingests.duckdb"),
        dataset_name=schema_name,
    )
    load_info = pipeline.run(source)
    return load_info


def write_source(config):
    SOURCES_PATH.mkdir(exist_ok=True)
    with open(SOURCES_PATH, "wb+") as file:
        yaml.safe_dump(config, file, encoding="utf-8")


def get_source_names():
    source_files = SOURCES_PATH.glob("**/*")
    return [file.stem for file in source_files if file.suffix == ".yaml"]


def get_source_path(name: str) -> Path:
    return SOURCES_PATH / f"{name}.yaml"


def read_source_config(source_name: str) -> RESTAPIConfig:
    source_path = get_source_path(source_name)
    return (
        RESTAPIConfig(**yaml.safe_load(source_path.read_text()))
        if source_path.exists()
        else RESTAPIConfig(
            client=ClientConfig(),
            resource_defaults=EndpointResourceBase(),
            resources=list(),
        )
    )


if __name__ == "__main__":
    print(get_source_names())
