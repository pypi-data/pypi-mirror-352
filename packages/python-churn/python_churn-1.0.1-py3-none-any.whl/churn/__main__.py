"""Executes tasks based on yaml configuration."""

import argparse
import logging
import os
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

import churn


def setup_logging(config: dict[str, Any]) -> None:
    """
    Set up logging for the application.

    Parameters
    ----------
    config : dict[str, Any]
        Configuration dictionary containing the output folder for logs.
    """
    log_formatter = logging.Formatter(logging.BASIC_FORMAT)
    root_logger = logging.getLogger()

    file_handler = logging.FileHandler(Path(config['output_folder']) / 'churn.log')
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    root_logger.setLevel(os.environ.get('LOGLEVEL', 'INFO').upper())


parser = argparse.ArgumentParser(
    description='Execute tasks based on yaml configuration.'
)

parser.add_argument(
    '--dry-run',
    action='store_true',
    help='Run the script in dry run mode without executing any tasks.',
)

parser.add_argument(
    'template_directory',
    type=Path,
    help='Path to the directory containing the template files.',
)

args = parser.parse_args()

with (args.template_directory / 'run.yaml').open() as config_file:
    config = yaml.safe_load(config_file)

setup_logging(config)
logger = logging.getLogger(__name__)

logger.info(
    'Loaded configuration from %s',
    args.template_directory / 'run.yaml',
)

churn.Configurator(
    config['context'],
    Path(config['output_folder']),
    args.template_directory,
).render()
logger.info(
    'Configuration rendered to %s',
    Path(config['output_folder']),
)


def task_generator(tasks: list[dict[str, Any]]) -> Iterable[churn.Task]:
    """
    Generate tasks from the configuration.

    Parameters
    ----------
    tasks : list[dict[str, Any]]
        List of tasks to generate.

    Returns
    -------
    Iterable[churn.Task]
        Generator of Task objects.
    """
    return (
        churn.Task(
            task['name'],
            args.template_directory,
            Path(config['output_folder']),
            list(map(Path, task['output_files'])),
            list(map(Path, task.get('extra_input_files', []))),
        )
        for task in tasks
    )


if not args.dry_run:
    if (pre_tasks := config.get('pre_tasks')) is not None:
        logger.info('Running pre-tasks')
        churn.run_chain(*task_generator(pre_tasks))
    logger.info('Running main tasks')
    churn.create_batch_chain(*task_generator(config['tasks']))
