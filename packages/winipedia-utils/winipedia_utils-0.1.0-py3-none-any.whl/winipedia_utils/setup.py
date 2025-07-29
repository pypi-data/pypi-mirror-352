"""A script that can be called after you installed the package.

This script calls create tests, creates the pre-commit config, and
creates the pyproject.toml file and some other things to set up a project.
This package assumes you are using poetry and pre-commit.
This script is intended to be called once at the beginning of a project.
"""

from winipedia_utils.git.pre_commit.config import _add_package_hook_to_pre_commit_config
from winipedia_utils.git.pre_commit.run_hooks import _run_all_hooks
from winipedia_utils.logging.logger import get_logger
from winipedia_utils.projects.poetry.config import (
    _add_tool_configurations_to_pyproject_toml,
)
from winipedia_utils.projects.poetry.poetry import (
    _install_dev_dependencies,
)

logger = get_logger(__name__)


def _setup() -> None:
    """Set up the project."""
    # install winipedia_utils dev dependencies as dev
    _install_dev_dependencies()
    # create pre-commit config
    _add_package_hook_to_pre_commit_config()
    # add tool.* configurations to pyproject.toml
    _add_tool_configurations_to_pyproject_toml()
    # run pre-commit once, create tests is included here
    _run_all_hooks()
    logger.info("Setup complete!")


if __name__ == "__main__":
    _setup()
