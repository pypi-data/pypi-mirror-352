import logging

from scorep_db.config import Config
from scorep_db.object_store import get_object_store
from scorep_db.rdf_database import get_rdf_database


def clear_function(config: Config):
    logging.info(
        f"Clearing databases and storage for "
        f"metadata mode '{config.metadata_mode}' and "
        f"record mode '{config.record_mode}'."
    )

    rdf_database = get_rdf_database(config, config.metadata_mode)
    object_store = get_object_store(config, config.record_mode)

    confirmation = input(
        f"Are you sure you want to clear all data in the following paths?\n"
        f"RDF Database: '{rdf_database.get_database_uri()}'\n"
        f"Object Store: '{object_store.get_storage_path()}'\n"
        f"This action cannot be undone. (yes/no): "
    )
    if confirmation.lower() != "yes":
        logging.info("Clear operation aborted by the user.")
        return

    logging.info("User confirmed. Proceeding with clearing operation.")

    # Clear RDF Database
    existing_graph = rdf_database.get_graph()
    existing_graph.remove((None, None, None))  # Remove all triples
    existing_graph.commit()
    existing_graph.close()
    logging.info("RDF database cleared.")

    # Clear Object Store
    object_store.clear_storage()
    logging.info("Object store cleared.")
