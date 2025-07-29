# -*- coding: utf-8 -*-

"""
table_step
A step for data tables in a SEAMM flowchart
"""

# Bring up the classes so that they appear to be directly in
# the table_step package.

from table_step.table import Table  # noqa: F401
from table_step.table_parameters import TableParameters  # noqa: F401
from table_step.table_step import TableStep  # noqa: F401
from table_step.tk_table import TkTable  # noqa: F401

# Handle versioneer
from ._version import get_versions

__author__ = """Paul Saxe"""
__email__ = "psaxe@molssi.org"
versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions
