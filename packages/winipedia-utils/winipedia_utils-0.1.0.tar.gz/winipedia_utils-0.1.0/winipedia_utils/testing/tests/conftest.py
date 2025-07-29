"""Pytest configuration for winipedia_utils tests.

finds all the plugins in the tests directory and the package's testing module
and adds them to pytest_plugins. This way defining reusable fixtures is easy.
"""

from winipedia_utils.consts import PACKAGE_NAME
from winipedia_utils.modules.module import to_module_name, to_path

custom_plugin_path = to_path("tests.base.fixtures", is_package=True)
package_plugin_path = (
    to_path(f"{PACKAGE_NAME}.testing", is_package=True) / custom_plugin_path
)

custom_plugin_module_names = [
    to_module_name(path) for path in custom_plugin_path.rglob("*.py")
]
package_plugin_module_names = [
    to_module_name(path) for path in package_plugin_path.rglob("*.py")
]


pytest_plugins = [
    *package_plugin_module_names,
    *custom_plugin_module_names,
]
