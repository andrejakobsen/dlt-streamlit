from pathlib import Path
from typing import Any

import dlt
import toml
import yaml
from rest_api import rest_api_source

ROOT_DIR = Path(__file__).parents[1]
SOURCES_PATH = ROOT_DIR / "sources"


def run_pipeline(source_name: str, schema_name: str):
    sources = read_source()
    source_config = sources["sources"][source_name]
    source = rest_api_source(source_config)

    pipeline = dlt.pipeline(
        pipeline_name=f"{source_name}_pipeline",
        destination=dlt.destinations.duckdb("dlt_ingests.duckdb"),
        dataset_name=schema_name,
    )
    load_info = pipeline.run(source)
    return load_info


def write_source(config):
    with open(SOURCES_PATH, "wb+") as file:
        yaml.safe_dump(config, file, encoding="utf-8")


def read_source(name: str) -> dict[str, Any]:
    SOURCES_PATH.mkdir(exist_ok=True)
    source_path = SOURCES_PATH / f"{name}.yaml"
    return yaml.safe_load(source_path.read_text()) if source_path.exists() else {}
