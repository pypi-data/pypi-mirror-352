"""Template repo"""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("rs-template")
except PackageNotFoundError:
    __version__ = "uninstalled"

__author__ = "Dennis Brookner"
__email__ = "debrookner@gmail.com"

from rs_template.python_library import fancy_read_cif, fancy_read_mtz
