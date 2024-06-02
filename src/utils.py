from pathlib import Path

import dlt
import toml
import yaml
from rest_api import rest_api_source

DLT_FOLDER = Path(__file__).parents[1] / ".dlt"
SOURCES_PATH = DLT_FOLDER / "sources.yaml"
SECRETS_PATH = DLT_FOLDER / "secrets.toml"


def run_pipeline(source_name: str, schema_name: str):
    sources = read_sources()
    source_config = sources["sources"][source_name]
    source = rest_api_source(source_config)

    pipeline = dlt.pipeline(
        pipeline_name=f"{source_name}_pipeline",
        destination=dlt.destinations.duckdb("dlt_ingests.duckdb"),
        dataset_name=schema_name,
    )
    load_info = pipeline.run(source)
    return load_info


def write_sources(config):
    with open(SOURCES_PATH, "wb+") as file:
        yaml.safe_dump(config, file, encoding="utf-8")


def read_sources():
    if not SOURCES_PATH.exists():
        return {"sources": {}}
    with open(SOURCES_PATH, "r") as file:
        return yaml.safe_load(file)


def read_secrets():
    with open(SECRETS_PATH, "r") as file:
        return toml.load(file)
