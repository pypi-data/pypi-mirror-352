import argparse
import logging
import os
from dataclasses import dataclass, fields
from distutils.util import strtobool
from enum import Enum
from pathlib import Path
from types import UnionType
from typing import Any, get_args, get_origin

from dotenv import dotenv_values

from scorep_db.exceptions import ConfigError

logger = logging.getLogger(__name__)


class Command(Enum):
    ADD = "add"
    MERGE = "merge"
    CLEAR = "clear"
    QUERY = "query"
    GET_ID = "get-id"
    DOWNLOAD = "download"
    HEALTH_CHECK = "health_check"
    PARSE = "parse"


class Mode(Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class RecordMode(Enum):
    LOCAL = "local"
    S3 = "s3"


class MetadataMode(Enum):
    SQLITE = "sqlite"
    RDF4J = "rdf4j"
    FUSEKI = "fuseki"


@dataclass
class Config:
    command: Command | None
    record_mode: RecordMode
    metadata_mode: MetadataMode
    experiment_path: Path
    append_files: list[Path]
    download_directory: Path | None
    query_file: Path | None
    dryrun: bool

    # Record Store
    record_local_directory: Path | None

    record_s3_hostname: str | None
    record_s3_port: int | None
    record_s3_user: str | None
    record_s3_password: str | None
    record_s3_bucket_name: str | None

    # Metadata Store
    metadata_sqlite_path: Path | None
    metadata_sqlite_name: str | None

    metadata_rdf4j_hostname: str | None
    metadata_rdf4j_port: int | None
    metadata_rdf4j_user: str | None
    metadata_rdf4j_password: str | None
    metadata_rdf4j_db_name: str | None

    metadata_fuseki_hostname: str | None
    metadata_fuseki_port: int | None
    metadata_fuseki_user: str | None
    metadata_fuseki_password: str | None
    metadata_fuseki_db_name: str | None

class ConfigFactory:
    """
    A factory class for building a Config object from multiple input sources.

    The ConfigFactory is responsible for collecting configuration data from various sources,
    such as command-line arguments, environment variables, .env files, and a dictionary-based
    configuration. It performs syntactic validation and prepares the data for the Config class.

    This class ensures that all inputs are properly normalized and type-checked before they
    are passed to the Config class, which handles semantic validation and enforces logical
    consistency between configuration fields.

    Attributes
    ----------
    env_prefix : str
        Prefix for environment variables. Defaults to "SCOREP_DB_".

    Parameters
    ----------
    cli_parse : bool, optional
        Whether to parse command-line arguments. Defaults to False.
    dict_config : dict, optional
        A dictionary containing configuration data, which overrides other sources. Defaults to None.
    raise_on_error : bool, optional
        Whether to raise an exception immediately if an error occurs during configuration processing. Defaults to False.

    Methods
    -------
    build() -> Config
        Builds and returns a validated Config object.
    _handle_error(error: Exception)
        Handles an error by either logging it or appending it to the errors list.
    _load_cli_args() -> argparse.Namespace
        Parses command-line arguments for the Scorep-DB tool.
    _load_system_env_variables() -> dict[str, str]
        Loads system environment variables.
    _load_dotenv_variables(path: Path | None) -> dict[str, str] | None
        Loads environment variables from a .env file.
    _load_config_file() -> dict[str, str] | None
        Loads configuration data from a file specified in 'config_file'.
    _get_config_value(name: str) -> Any | None
        Retrieves a configuration value from CLI, dictionary config, .env, or environment variables.
    _gather_config() -> dict[str, Any]
        Collects and prepares configuration values for building a Config object.
    _parse_validate_value(field_name: str, raw_value, field_type) -> Any | None
        Parses and validates a raw configuration value to the appropriate type based on the specified field type.

    Raises
    ------
    ConfigError
        If any errors occur during loading, parsing, or casting configuration values.
    """

    env_prefix = "SCOREP_DB_"

    def __init__(
        self,
        cli_parse: bool = False,
        dict_config: dict | None = None,
        raise_on_error: bool = False,
    ):
        self.errors: list[Exception] = []
        self.raise_on_error: bool = raise_on_error

        if dict_config is None:
            self._dict_config = {}
        elif isinstance(dict_config, dict):
            self._dict_config = dict_config
        else:
            logger.warning(
                "Invalid type for 'dict_config'. Expected dict, got %s.",
                type(dict_config),
            )
            self._dict_config = {}

        if cli_parse:
            self._cli_args: argparse.Namespace = self._load_cli_args()
        else:
            self._cli_args = argparse.Namespace()

        self._env_vars = self._load_system_env_variables()

        self._dotenv_vars = {}
        self._dotenv_vars = self._load_config_file()

    def build(self) -> Config:
        """
        Builds the configuration object from the CLI arguments and environment variables.

        Returns
        -------
        Config
            A Config object with all values cast to their expected types.

        Raises
        ------
        ConfigError
            If any errors occur during loading, parsing, or casting configuration values.
        """
        raw_config = self._gather_config()
        if self.errors and self.raise_on_error:
            raise ConfigError(f"Configuration errors occurred: {self.errors}")
        elif self.errors:
            logger.warning("Configuration errors occurred: %s", self.errors)
        else:
            logger.info("Configuration loaded successfully. Building Config object...")

        try:
            config = Config(**raw_config)
            logger.debug("Config object created successfully.\n%s", config)
            return config
        except Exception as e:
            raise ConfigError(f"Failed to build Config object: {e}")

    def _handle_error(self, error: Exception):
        """
        Handles an error by either logging it or appending it to the errors list.

        Parameters
        ----------
        error : Exception
            The exception to handle.
        """
        self.errors.append(error)
        logger.error(error)

    def _load_cli_args(self) -> argparse.Namespace:
        """
        Parses CLI arguments for the Scorep-DB Command Line Tool.

        Returns
        -------
        argparse.Namespace
            Parsed command line arguments.
        """
        # Define arguments
        arg_config_file = lambda arg_parser, positional=False: arg_parser.add_argument(
            "config_file" if positional else "--config-file",
            help="Path to config file",
        )
        arg_record_mode = lambda arg_parser, positional=False: arg_parser.add_argument(
            "record_mode" if positional else "--record-mode",
            choices=[mode.value for mode in RecordMode],
            help="Record store mode",
        )
        arg_metadata_mode = (
            lambda arg_parser, positional=False: arg_parser.add_argument(
                "metadata_mode" if positional else "--metadata-mode",
                choices=[mode.value for mode in MetadataMode],
                help="Metadata store mode",
            )
        )
        arg_experiment_path = (
            lambda arg_parser, positional=False: arg_parser.add_argument(
                "experiment_path" if positional else "--experiment-path",
                help="Path to Scorep experiment",
            )
        )
        arg_query_file = lambda arg_parser, positional=False: arg_parser.add_argument(
            "query_file" if positional else "--query-file",
            help="Path to SPARQL query file",
        )
        arg_append_files = lambda arg_parser, positional=False: arg_parser.add_argument(
            "append_files" if positional else "--append-files",
            nargs="*",
            help="Additional JSON-LD files to append and merge",
        )
        arg_download_directory = (
            lambda arg_parser, positional=False: arg_parser.add_argument(
                "download_directory" if positional else "--download-directory",
                help="Path to the downloaded files",
            )
        )
        arg_dryrun = lambda arg_parser, positional=False: arg_parser.add_argument(
            "dryrun" if positional else "--dryrun",
            action="store_true",
            help="Simulate the process without making changes",
        )

        # Create parser
        parser = argparse.ArgumentParser(
            prog="scorep-db", description="Scorep-DB Command Line Tool"
        )
        subparsers = parser.add_subparsers(dest="command", required=True)

        parser_add = subparsers.add_parser(
            Command.ADD.value,
            help="Add a Scorep experiment",
        )
        arg_config_file(parser_add)
        arg_record_mode(parser_add)
        arg_metadata_mode(parser_add)
        arg_experiment_path(parser_add, True)
        arg_append_files(parser_add)

        parser_merge = subparsers.add_parser(
            Command.MERGE.value,
            help="Merge an offline database into an online database",
        )
        arg_config_file(parser_merge)
        arg_dryrun(parser_merge)

        parser_clear = subparsers.add_parser(
            Command.CLEAR.value,
            help="Clear the databases and storage",
        )
        arg_config_file(parser_clear)
        arg_record_mode(parser_clear)
        arg_metadata_mode(parser_clear)

        parser_query = subparsers.add_parser(
            Command.QUERY.value,
            help="Execute a SPARQL query on the RDF database",
        )
        arg_config_file(parser_query)
        arg_record_mode(parser_query)
        arg_metadata_mode(parser_query)
        arg_query_file(parser_query, True)

        parser_get_id = subparsers.add_parser(
            Command.GET_ID.value,
            help="Add a Scorep experiment",
        )
        arg_config_file(parser_get_id)
        arg_experiment_path(parser_get_id, True)

        parser_download = subparsers.add_parser(
            Command.DOWNLOAD.value,
            help="Download the experiments that are the result of a SPARQL query",
        )
        arg_config_file(parser_download)
        arg_record_mode(parser_download)
        arg_metadata_mode(parser_download)
        arg_query_file(parser_download, True)
        arg_download_directory(parser_download, True)
        arg_dryrun(parser_download)

        parser_health_check = subparsers.add_parser(
            Command.HEALTH_CHECK.value,
            help="Verify database accessibility",
        )
        arg_config_file(parser_health_check)
        arg_record_mode(parser_health_check)
        arg_metadata_mode(parser_health_check)

        parser_parse = subparsers.add_parser(
            Command.PARSE.value,
            help="Parse json-ld file to stdout",
        )
        arg_experiment_path(parser_parse, True)
        arg_append_files(parser_parse)

        try:
            return parser.parse_args()
        except argparse.ArgumentError as e:
            self._handle_error(ConfigError(f"Failed to parse CLI arguments: {e}"))
            return argparse.Namespace()

    # noinspection PyMethodMayBeStatic
    def _load_system_env_variables(self) -> dict[str, str]:
        """
        Loads system environment variables

        Returns
        -------
        dict[str, Any]
            A dictionary with environment variables.
        """
        return dict(os.environ)

    def _load_dotenv_variables(self, path: Path | None) -> dict[str, str]:
        """
        Loads environment variables from a .env file.

        Parameters
        ----------
        path : Path | None
            Path to the .env file. If None, it will look for a .env file in the current working directory.

        Returns
        -------
        dict[str, str]
            A dictionary with environment variables from the .env file, or an empty dictionary if loading fails.
        """
        if path is None:
            path = Path.cwd() / ".env"
        elif isinstance(path, (str, os.PathLike)):
            path = Path(path)
        else:
            logger.error(
                "Unsupported dotenv path type, expected Path or str, got %s",
                type(path),
            )
            return {}

        if path.exists() and path.is_file():
            try:
                logger.info("Found .env file: %s", path)
                result = dotenv_values(path)
                return dict(result)
            except (FileNotFoundError, PermissionError) as e:
                logger.error("Error loading .env file: %s", e)
                return {}
            except UnicodeDecodeError as e:
                self._handle_error(
                    ConfigError("Invalid characters in .env file: %s" % e)
                )
                return {}
        else:
            logger.info("No .env file or configuration file found at '%s'.", path)
            return {}

    def _load_config_file(self) -> dict[str, str]:
        """
        Loads environment variables from a config file specified in 'config_file'.
        If no config file is provided, it falls back to the default .env loading logic.

        Returns
        -------
        dict[str, str]
            A dictionary with environment variables from the specified config file.
        """
        config_path = self._get_config_value("config_file")
        config_path = self._parse_validate_value("config_file", config_path, Path)

        return self._load_dotenv_variables(config_path)

    def _get_config_value(self, name: str) -> Any | None:
        """
        Retrieves the value from CLI arguments, dictionary config, environment variables, and dotenv, in that order.

        Parameters
        ----------
        name : str
            The name of the configuration field to retrieve.

        Returns
        -------
        Any | None
            The resolved configuration value from CLI, dictionary config, dotenv, or environment variables.
        """
        cli_value = getattr(self._cli_args, name, None)
        if cli_value is not None and cli_value != "":
            return cli_value

        dict_value = self._dict_config.get(name)
        if dict_value is not None and dict_value != "":
            return dict_value

        env_key = self.env_prefix + name.upper()

        dotenv_value = self._dotenv_vars.get(env_key)
        if dotenv_value is not None and dotenv_value != "":
            return dotenv_value

        env_value = self._env_vars.get(env_key)
        if env_value is not None and env_value != "":
            return env_value

        return None

    def _gather_config(self) -> dict[str, Any]:
        """
        Collects and casts configuration values from various sources
        (CLI, dictionary config, dotenv, and environment variables)
        into a dictionary based on the fields defined in the Config dataclass.

        Returns
        -------
        dict[str, Any]
            A dictionary where each key corresponds to a field in Config,
            and each value is cast to the correct type.
        """
        config = {}

        for field in fields(Config):  # type: ignore[arg-type]
            raw_value = self._get_config_value(field.name)
            try:
                config[field.name] = self._parse_validate_value(
                    field.name, raw_value, field.type
                )
            except ConfigError as e:
                self._handle_error(e)

        return config

    # noinspection PyMethodMayBeStatic
    def _parse_validate_value(
        self, field_name: str, raw_value, field_type
    ) -> Any | None:
        """
        Parses and validates a raw configuration value to the appropriate type based on the specified field type.

        Parameters
        ----------
        field_name : str
            The name of the field to cast, used for logging in case of error.
        raw_value : Any
            The raw configuration value to cast.
        field_type : type
            The expected type of the field to which raw_value should be cast.

        Returns
        -------
        Any | None
            The value cast to the specified field_type, or None if raw_value is None.

        Raises
        ------
        ConfigError
            If the raw_value cannot be cast to the specified field_type.
        """
        if raw_value is None:
            return None

        none_str = ["None", "NULL", "NaN", ""]  # case-insensitive
        if raw_value in none_str:
            return None

        # Check for Union types i.e. Optional
        if get_origin(field_type) is UnionType:
            types_in_union = [t for t in get_args(field_type) if t is not type(None)]
            for sub_type in types_in_union:
                try:
                    return self._parse_validate_value(field_name, raw_value, sub_type)
                except ConfigError:
                    continue
            raise ConfigError(
                f"Failed to parse '{field_name}' with value '{raw_value}' to any type in {field_type}."
            )

        try:
            # Handle lists of Paths
            if get_origin(field_type) == list:
                item_type = get_args(field_type)[0]
                if item_type in {Path, str, os.PathLike}:
                    return [
                        self._parse_validate_value(field_name, item, item_type)
                        for item in (
                            raw_value
                            if isinstance(raw_value, list)
                            else raw_value.split(",")
                        )
                    ]
                else:
                    raise ValueError(
                        f"Unsupported list item type '{item_type}' for field '{field_name}'."
                    )

            elif field_type == Path:
                if isinstance(raw_value, (str, os.PathLike)):
                    return Path(raw_value).resolve()
                else:
                    raise ValueError(f"Invalid path value: {raw_value}")

            elif field_type == bool:
                if isinstance(raw_value, bool):
                    return raw_value
                elif isinstance(raw_value, str):
                    return strtobool(raw_value)
                elif isinstance(raw_value, (int, float)):
                    return bool(raw_value)
                else:
                    raise ValueError(f"Invalid boolean value: {raw_value}")

            elif issubclass(field_type, Enum):
                if isinstance(raw_value, field_type):
                    return raw_value
                if isinstance(raw_value, str):
                    try:
                        return field_type(raw_value)
                    except ValueError:
                        raise ValueError(
                            f"Invalid value '{raw_value}' for enum {field_type.__name__}."
                        )

            elif field_type in [int, float, str]:
                return field_type(raw_value)

            return field_type(raw_value)

        except (ValueError, TypeError) as e:
            raise ConfigError(
                f"Failed to cast '{field_name}' with value '{raw_value}' to {field_type}: {e}"
            )
        except Exception as e:
            raise ConfigError(
                f"Unexpected error casting '{field_name}' with value '{raw_value}' to {field_type}: {e}"
            )
