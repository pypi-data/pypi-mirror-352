import logging
from pathlib import Path

from rdflib import Graph

from scorep_db.config import Config
from scorep_db.rdf_helper import (
    SCOREP_JSONLD_FILE,
)


def handle_parse(
    experiment_path: Path|None,
    metadata_file_name: str,
    append_files: list[Path] = None,
) -> None:
    new_graph = None

    if experiment_path is not None:
        new_graph = Graph().parse(
            str(experiment_path / metadata_file_name),
            format="json-ld",
        )

    # Parse and merge additional JSON-LD files if provided
    if append_files:
        for file_path in append_files:
            logging.info(f"Appending JSON-LD file: {file_path}")
            if new_graph is None:
                new_graph = Graph().parse(str(file_path), format="json-ld")
            else:
                additional_graph = Graph().parse(str(file_path), format="json-ld")
                new_graph += additional_graph

    new_graph.commit()

    turtle_data = new_graph.serialize(format="turtle")
    print(turtle_data)

    new_graph.close()


def parse_function(config: Config):
    metadata_file_name = SCOREP_JSONLD_FILE

    experiment_path: Path = config.experiment_path

    append_files: list[Path] = config.append_files if config.append_files else []

    if experiment_path is not None:
        if not experiment_path.exists():
            logging.error(
                f"Experiment path '{experiment_path}' does not exist. Aborting."
            )
            return

        metadata_file = experiment_path / metadata_file_name
        if metadata_file is None or not metadata_file.exists():
            logging.error(f"Metadata file '{metadata_file}' does not exist. Aborting.")
            return
        elif metadata_file.stat().st_size == 0:
            logging.error(f"Metadata file '{metadata_file}' is empty. Aborting.")
            return

    logging.info(
        f"Parsing experiment with metadata mode: {config.metadata_mode}, "
        f"record mode: {config.record_mode}, path: {experiment_path}"
    )
    handle_parse(experiment_path, metadata_file_name, append_files)
