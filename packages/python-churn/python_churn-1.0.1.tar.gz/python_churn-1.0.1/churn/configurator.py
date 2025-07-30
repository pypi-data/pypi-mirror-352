"""Contains class to configure everything for running the tools."""

import filecmp
import logging
import shutil
from pathlib import Path
from typing import Any

import jinja2

logger = logging.getLogger(__name__)


class Configurator:  # pylint: disable=too-few-public-methods
    """
    Creates the configuration for the mesh and the solver.

    Essentially just substitutes the required variables into the jinja2 templates.

    Attributes
    ----------
    context : dict[str, Any]
        Dictionary containing the context for the jinja2 templates.
    output_folder : Path
        Path to the folder where the rendered templates will be saved.
    input_folder : Path
        Path to the folder containing the jinja2 templates and other files to copy.
    """

    def __init__(
        self, context: dict[str, Any], output_folder: Path, input_folder: Path
    ):
        """
        Create a Configurator object.

        Parameters
        ----------
        context : dict[str, Any]
            Dictionary containing the context for the jinja2 templates.
        output_folder : Path
            Path to the folder where the rendered templates will be saved.
        input_folder : Path
            Path to the folder containing the jinja2 templates.
        """
        self.context = context
        self.input_folder = input_folder
        self.output_folder = output_folder
        self._env = jinja2.Environment(  # noqa: S701
            loader=jinja2.FileSystemLoader(str(input_folder))
        )

    def render(self) -> None:
        """
        Render all templates in the input folder and saves them to the output folder.

        Non-template files or directories are copied as is. Only changed files are
        replaced.
        """
        for task in self.input_folder.iterdir():
            if not task.is_dir():
                continue
            (self.output_folder / task.name).mkdir(exist_ok=True, parents=True)
            for template in task.rglob('*'):
                if template.is_file():
                    rel_path = template.relative_to(self.input_folder)
                    if template.suffix == '.j2':
                        self._render_template(rel_path)
                    else:
                        output_path = self.output_folder / rel_path
                        if not output_path.exists() or not filecmp.cmp(
                            template, output_path
                        ):
                            logger.debug(
                                'Copying file %s to %s',
                                template,
                                output_path,
                            )
                            shutil.copy(template, output_path)
                elif template.is_dir():
                    (
                        self.output_folder / template.relative_to(self.input_folder)
                    ).mkdir(exist_ok=True)

    def _render_template(self, rel_path: Path) -> None:
        output_path = self.output_folder / rel_path.with_suffix('')
        result = self._env.get_template(str(rel_path)).render(**self.context)

        if output_path.exists():
            with output_path.open('r') as output_file:
                contents = output_file.read()
        else:
            contents = ''

        if contents != result:
            logger.debug(
                'Rendering template %s to %s',
                self.input_folder / rel_path,
                output_path,
            )
            with output_path.open('w') as output_file:
                output_file.write(result)
            shutil.copymode(self.input_folder / rel_path, output_path)
