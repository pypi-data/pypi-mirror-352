import logging

from scorep_db.command_add import add_function
from scorep_db.command_clear import clear_function
from scorep_db.command_download import download_function
from scorep_db.command_get_id import get_id_function
from scorep_db.command_health_check import health_check_function
from scorep_db.command_merge import merge_function
from scorep_db.command_query import query_function
from scorep_db.command_parse import parse_function
from scorep_db.config import Command, ConfigFactory


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    config = ConfigFactory(cli_parse=True, raise_on_error=True).build()

    if config.command is None:
        logging.error("No command provided. Exiting.")
        return

    mapping = {
        Command.ADD: add_function,
        Command.MERGE: merge_function,
        Command.CLEAR: clear_function,
        Command.QUERY: query_function,
        Command.GET_ID: get_id_function,
        Command.DOWNLOAD: download_function,
        Command.HEALTH_CHECK: health_check_function,
        Command.PARSE: parse_function,
    }

    func = mapping.get(config.command, None)
    if func is not None:
        func(config)


if __name__ == "__main__":
    main()
