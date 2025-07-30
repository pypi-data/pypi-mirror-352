"""Utilities for working with Python projects."""

from winipedia_utils.modules.module import create_module, to_path
from winipedia_utils.modules.package import get_src_package
from winipedia_utils.projects.poetry.config import get_poetry_package_name


def _create_project_root() -> None:
    """Create the project root."""
    src_package_name = get_poetry_package_name()
    create_module(src_package_name, is_package=True)
    _create_py_typed()


def _create_py_typed() -> None:
    """Create the py.typed file."""
    src_package_name = get_src_package().__name__
    py_typed_path = to_path(src_package_name, is_package=True) / "py.typed"
    py_typed_path.touch()
