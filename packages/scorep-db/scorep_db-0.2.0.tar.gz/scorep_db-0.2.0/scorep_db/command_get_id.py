import json
import logging
import sys
from pathlib import Path

from rdflib import RDF, Graph

from scorep_db.config import Config
from scorep_db.rdf_helper import SCOREP, SCOREP_JSONLD_FILE


def handle_get_id(experiment_path, metadata_file_name) -> bool:
    #new_graph = Graph().parse(
    #    str(experiment_path / metadata_file_name), format="json-ld"
    #)

    #subject = list(new_graph.subjects(predicate=RDF.type, object=SCOREP.ExperimentRun))
    #assert len(subject) == 1
    #subject = subject[0]

    #print(str(subject))
    with open(experiment_path / metadata_file_name) as f:
        json_data = json.load(f)

    id = json_data.get("id", None)
    if id is None:
        sys.exit(1)

    print(id)


def get_id_function(config: Config):
    metadata_file_name = SCOREP_JSONLD_FILE

    experiment_path: Path = config.experiment_path

    if not experiment_path.exists():
        logging.error(f"Experiment path '{experiment_path}' does not exist. Aborting.")
        return

    metadata_file = experiment_path / metadata_file_name
    if not metadata_file.exists():
        logging.error(f"Metadata file '{metadata_file}' does not exist. Aborting.")
        return
    elif metadata_file.stat().st_size == 0:
        logging.error(f"Metadata file '{metadata_file}' is empty. Aborting.")
        return

    handle_get_id(experiment_path, metadata_file_name)
