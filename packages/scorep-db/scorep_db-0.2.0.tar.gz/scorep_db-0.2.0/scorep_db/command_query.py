import logging
from pathlib import Path

from scorep_db.config import Config
from scorep_db.rdf_database import get_rdf_database


def query_function(config: Config):
    query_file: Path = config.query_file

    if query_file is None or not query_file.exists():
        logging.error(f"Query file '{query_file}' does not exist. Aborting.")
        return

    # Read the query
    with query_file.open("r", encoding="utf-8") as file:
        sparql_query = file.read()

    logging.info(f"Executing SPARQL query from file: {query_file}")

    # Connect to the RDF database
    rdf_database = get_rdf_database(config, config.metadata_mode).get_graph()

    # Execute the query
    try:
        results = rdf_database.query(sparql_query)

        for i, row in enumerate(results, start=1):
            print(f"Result {i}:")
            for var in row.labels:
                print(f"  {var}: {row[var]}")
            print("-" * 40)

        logging.info("Query executed successfully.")

    except Exception as e:
        logging.error(f"Failed to execute query: {e}")

    finally:
        rdf_database.close()
