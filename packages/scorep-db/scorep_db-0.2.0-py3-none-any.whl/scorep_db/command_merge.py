import logging
from pathlib import Path

from rdflib import RDF, Graph

from scorep_db.config import Config, MetadataMode, RecordMode
from scorep_db.object_store import get_object_store
from scorep_db.rdf_database import get_rdf_database
from scorep_db.rdf_helper import SCOREP


def handle_merge(config: Config, dryrun: bool = False):
    local_rdf_db: Graph = get_rdf_database(config, MetadataMode.SQLITE).get_graph()
    #remote_rdf_db: Graph = get_rdf_database(config, MetadataMode.RDF4J).get_graph()
    remote_rdf_db: Graph = get_rdf_database(config, MetadataMode.FUSEKI).get_graph()

    local_object_store = get_object_store(config, RecordMode.LOCAL)
    remote_object_store = get_object_store(config, RecordMode.S3)

    local_experiments = list(
        local_rdf_db.subjects(predicate=RDF.type, object=SCOREP.ExperimentRun)
    )
    assert len(local_experiments) > 1

    for local_experiment in local_experiments:
        if (local_experiment, RDF.type, SCOREP.ExperimentRun) in remote_rdf_db:
            continue
        if not local_experiment:
            print("None local experiment")

            continue

        store_location = None
        for obj in local_rdf_db.objects(
            subject=local_experiment, predicate=SCOREP.storeLocation
        ):
            store_location = obj
            break
        print(f"{store_location=}")
        if not store_location:
            logging.error(
                f"Entry '{local_experiment}' has no 'storeLocation'! This should not have happened."
            )
            raise ValueError

        local_store_location = Path(str(store_location))

        local_db_root = Path(local_object_store.get_storage_path())
        # Reuse the old name for upload.
        # Directly upload the files without moving them into a local storage

        if dryrun:
            logging.info(f"Dryrun: Would upload {local_experiment}.")
        else:
            logging.info(f"Upload {local_experiment}.")
            remote_object_store.upload_experiment(
                local_db_root / local_store_location, local_store_location
            )

    if dryrun:
        logging.info("Dryrun: Would merge graphs.")
    else:
        logging.info("Merging graphs.")
        remote_rdf_db += local_rdf_db
        remote_rdf_db.commit()

    remote_rdf_db.close()
    local_rdf_db.close()

    return


def merge_function(config: Config):
    dryrun: bool = config.dryrun

    handle_merge(config, dryrun)
