import logging

from scorep_db.config import Config
from scorep_db.object_store import get_object_store
from scorep_db.rdf_database import get_rdf_database

logger = logging.getLogger(__name__)


def health_check_function(config: Config) -> None:
    db_result = get_rdf_database(config, config.metadata_mode).health_check()
    store_result = get_object_store(config, config.record_mode).health_check()

    if db_result and store_result:
        logging.info("Health check successful")
    else:
        logging.error("Health check failed")
        exit(1)
