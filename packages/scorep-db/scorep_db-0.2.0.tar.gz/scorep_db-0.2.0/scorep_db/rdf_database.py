import contextlib
import logging
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path

from rdflib import BNode, Graph, URIRef
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore, _node_to_sparql
from rdflib_sqlalchemy import registerplugins
from rdflib_sqlalchemy.store import SQLAlchemy

from scorep_db.config import Config, MetadataMode

logger = logging.getLogger(__name__)

registerplugins()


class RDFDatabase(ABC):
    static_identifier = URIRef("http://internal.scorep.org/")

    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    def get_graph(self) -> Graph:
        pass

    @abstractmethod
    def get_database_uri(self) -> str:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the RDF database is reachable and configured correctly."""
        pass


class SqliteRDFDatabase(RDFDatabase):
    def __init__(self, config: Config):
        super().__init__(config)

        scorep_db_path = config.metadata_sqlite_path
        assert scorep_db_path is not None
        self.scorep_db_path = Path(scorep_db_path)

        scorep_db_name = config.metadata_sqlite_name
        assert scorep_db_name is not None
        self.scorep_db_name = Path(scorep_db_name)

    def get_graph(self) -> Graph:
        logger.info("Connecting to offline database at '%s'", self.get_database_uri())

        def open_graph(db_path_: str) -> Graph:
            with contextlib.suppress(TypeError):
                store = SQLAlchemy(identifier=None)
                graph = Graph(store=store, identifier=self.static_identifier)

            # try:
            #     graph.open(db_path_, create=False)
            # except RuntimeError:
            graph.open(db_path_, create=True)

            return graph

        return open_graph(self.get_database_uri())

    def get_database_uri(self) -> str:
        return "sqlite:///" + self._get_database_path().as_posix()

    def _get_database_path(self) -> Path:
        return self.scorep_db_path / self.scorep_db_name

    def health_check(self):
        """Check if the SQLite RDF database file exists and is accessible."""
        db_path = Path(self._get_database_path())
        db_uri = self.get_database_uri()

        # 1) File existence
        if not db_path.exists():
            parent_dir = db_path.parent or Path('.')

            # Try to create & remove a temp file to verify writability
            test_file = parent_dir / '.tmp_write_test'
            try:
                with test_file.open('w'):
                    pass
                test_file.unlink()
                logger.warning(
                    "Offline RDF database file '%s' does not exist, "
                    "but directory '%s' is writable; a new database will be created on first use.",
                    db_uri,
                    parent_dir,
                )
                return True
            except Exception:
                logger.error(
                    "Offline RDF database file '%s' is inaccessible and "
                    "directory '%s' is not writable.",
                    db_uri,
                    parent_dir,
                )
                return False

        # 2) Connectivity & validity
        try:
            # str(db_path) because sqlite3.connect doesn’t accept Path on older Pythons
            with sqlite3.connect(str(db_path)) as conn:
                pass
        except sqlite3.DatabaseError as e:
            logger.error(
                "Offline RDF database file '%s' exists but is not a valid "
                "SQLite database: %s",
                db_uri,
                e,
            )
            return False

        logger.info(
            "Successfully checked offline RDF database file '%s'.",
            db_uri,
        )
        return True


class Rdf4jRDFDatabase(RDFDatabase):
    def __init__(self, config: Config):
        super().__init__(config)

        hostname = config.metadata_rdf4j_hostname
        assert hostname is not None
        self.hostname = hostname

        port = config.metadata_rdf4j_port
        assert port is not None
        self.port = port

        user = config.metadata_rdf4j_user
        assert user is not None
        self.user = user

        password = config.metadata_rdf4j_password
        assert password is not None
        self.password = password

        scorep_db_name = config.metadata_rdf4j_db_name
        assert scorep_db_name is not None
        self.scorep_db_name = scorep_db_name

    def get_graph(self) -> Graph:
        endpoint = self.get_database_uri()
        logging.info(f"Connecting to online database at '{endpoint}'")

        def my_bnode_ext(node):
            if isinstance(node, BNode):
                return f"<bnode:b{node}>"

            return _node_to_sparql(node)

        # Define the SPARQL endpoint URL for updates
        store = SPARQLUpdateStore(
            query_endpoint=endpoint,
            update_endpoint=endpoint + "/statements",
            # auth=(self.user, self.password), # Check here for security: https://rdf4j.org/documentation/tools/server-workbench/
            node_to_sparql=my_bnode_ext,
        )

        graph = Graph(
            store=store,
            identifier=self.static_identifier,
            bind_namespaces="none",
        )

        return graph

    def get_database_uri(self) -> str:
        # Define the SPARQL endpoint URL for updates
        return f"http://{self.hostname}:{self.port}/rdf4j-server/repositories/{self.scorep_db_name}"

    def health_check(self) -> bool:
        endpoint = self.get_database_uri()
        logger.info("Performing health check on RDF4J database at '%s'", endpoint)

        try:
            graph = self.get_graph()
            # if get_graph() succeeds, we consider the endpoint reachable
            graph.close()
            logger.info(
                "Successfully connected to RDF4J database at '%s'.", endpoint
            )
            return True

        except Exception as e:
            logger.error(
                "Failed to connect to RDF4J database at '%s': %s",
                endpoint,
                e,
            )
            return False


class FusekiRDFDatabase(RDFDatabase):
    def __init__(self, config: Config):
        super().__init__(config)

        hostname = config.metadata_fuseki_hostname
        assert hostname is not None
        self.hostname = hostname

        port = config.metadata_fuseki_port
        assert port is not None
        self.port = port

        user = config.metadata_fuseki_user
        assert user is not None
        self.user = user

        password = config.metadata_fuseki_password
        assert password is not None
        self.password = password

        scorep_db_name = config.metadata_fuseki_db_name
        assert scorep_db_name is not None
        self.scorep_db_name = scorep_db_name

    def get_graph(self) -> Graph:
        endpoint = self.get_database_uri()
        logging.info(f"Connecting to online database at '{endpoint}'")

        def my_bnode_ext(node):
            if isinstance(node, BNode):
                return f"<bnode:b{node}>"

            return _node_to_sparql(node)

        # Define the SPARQL endpoint URL for query and updates
        store = SPARQLUpdateStore(
            query_endpoint=endpoint + "/sparql",
            update_endpoint=endpoint + "/update",
            auth=(self.user, self.password),
            node_to_sparql=my_bnode_ext,
        )

        graph = Graph(
            store=store,
            identifier=self.static_identifier,
            bind_namespaces="none",
        )

        return graph

    def get_database_uri(self) -> str:
        # Define the SPARQL endpoint URL
        return f"http://{self.hostname}:{self.port}/{self.scorep_db_name}"

    def health_check(self) -> bool:
        endpoint = self.get_database_uri()
        logger.info("Performing health check on Fuseki database at '%s'", endpoint)

        try:
            graph = self.get_graph()
            # if get_graph() succeeds, we consider the endpoint reachable
            graph.close()
            logger.info(
                "Successfully connected to Fuseki database at '%s'.", endpoint
            )
            return True

        except Exception as e:
            logger.error(
                "Failed to connect to Fuseki database at '%s': %s",
                endpoint,
                e,
            )
            return False

def get_rdf_database(config: Config, mode: MetadataMode) -> RDFDatabase:
    if mode == MetadataMode.SQLITE:
        return SqliteRDFDatabase(config)
    elif mode == MetadataMode.RDF4J:
        return Rdf4jRDFDatabase(config)
    elif mode == MetadataMode.FUSEKI:
        return FusekiRDFDatabase(config)
    else:
        logging.error("Unknown mode '%s'. Aborting.", mode)
        raise ValueError(f"Unknown mode '{mode}'")
