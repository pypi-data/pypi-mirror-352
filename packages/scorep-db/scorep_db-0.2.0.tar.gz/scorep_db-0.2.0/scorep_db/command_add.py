import logging
from pathlib import Path, PurePosixPath

from rdflib import RDF, Graph, Literal

from scorep_db.config import Config
from scorep_db.object_store import get_object_store
from scorep_db.rdf_database import get_rdf_database
from scorep_db.rdf_helper import (
    SCOREP,
    SCOREP_JSONLD_FILE,
    test_if_already_exists,
)


def handle_add(
    config: Config,
    experiment_path: Path,
    metadata_file_name: str,
    append_files: list[Path] = None,
) -> None:
    rdf_database = get_rdf_database(config, config.metadata_mode)
    object_store = get_object_store(config, config.record_mode)

    existing_graph = rdf_database.get_graph()

    new_graph = Graph().parse(
        str(experiment_path / metadata_file_name), format="json-ld"
    )

    # Parse and merge additional JSON-LD files if provided
    if append_files:
        for file_path in append_files:
            logging.info(f"Appending JSON-LD file: {file_path}")
            additional_graph = Graph().parse(str(file_path), format="json-ld")
            new_graph += additional_graph

        #turtle_data = new_graph.serialize(format="turtle")
        #print(turtle_data, flush=True)

    already_merged = test_if_already_exists(
        existing_graph, new_graph, SCOREP.ExperimentRun
    )

    if already_merged:
        new_graph.close()
        existing_graph.close()
        return

    #new_experiment_directory_path = object_store.generate_new_experiment_path()

    subject = list(new_graph.subjects(predicate=RDF.type, object=SCOREP.ExperimentRun))[0]

    uuid = PurePosixPath(str(subject)).name
    new_experiment_directory_path = uuid

    new_graph.add((subject, SCOREP.storeLocation, Literal(new_experiment_directory_path)))

    new_graph.commit()

    logging.info(f"Added new attribute to '{subject}'")

    object_store.upload_experiment(experiment_path, new_experiment_directory_path)

    existing_graph += new_graph

    existing_graph.commit()
    existing_graph.close()
    new_graph.close()


def add_function(config: Config):
    metadata_file_name = SCOREP_JSONLD_FILE

    experiment_path: Path = config.experiment_path

    append_files: list[Path] = config.append_files if config.append_files else []

    if experiment_path is None or not experiment_path.exists():
        logging.error(f"Experiment path '{experiment_path}' does not exist. Aborting.")
        return

    metadata_file = experiment_path / metadata_file_name
    if metadata_file is None or not metadata_file.exists():
        logging.error(f"Metadata file '{metadata_file}' does not exist. Aborting.")
        return
    elif metadata_file.stat().st_size == 0:
        logging.error(f"Metadata file '{metadata_file}' is empty. Aborting.")
        return

    logging.info(
        f"Adding experiment with metadata mode: {config.metadata_mode}, "
        f"record mode: {config.record_mode}, path: {experiment_path}"
    )
    handle_add(config, experiment_path, metadata_file_name, append_files)
