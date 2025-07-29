import logging

from rdflib import RDF, Graph, Namespace, URIRef

SCOREP = Namespace("http://scorep-fair.github.io/schema/v0.1/ontology.ttl#")
SCOREP_JSONLD_FILE = "scorep.fair.json"


def test_if_already_exists(database: Graph, new_entry: Graph, key: URIRef) -> bool:
    subject = list(new_entry.subjects(predicate=RDF.type, object=key))
    print(subject, flush=True)
    assert len(subject) == 1
    subject = subject[0]

    if (subject, RDF.type, SCOREP.ExperimentRun) in database:
        logging.info(f"The subject '{subject}' already exists in the existing graph.")
        return True
    else:
        logging.info(f"The subject '{subject}' does not exist in the existing graph.")
        return False
