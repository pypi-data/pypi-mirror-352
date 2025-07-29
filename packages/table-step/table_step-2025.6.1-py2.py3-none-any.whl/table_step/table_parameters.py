# -*- coding: utf-8 -*-
"""Control parameters for tables"""

import logging
import seamm

logger = logging.getLogger(__name__)


class TableParameters(seamm.Parameters):
    """The control parameters for tables"""

    parameters = {
        "method": {
            "default": "Create",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": (
                "Create",
                "Read",
                "Save",
                "Save as",
                "Print",
                "Print the current row of",
                "Append a row to",
                "Go to the next row of",
                "Add columns to",
                "Set element of",
                "Get element of",
            ),
            "format_string": "s",
            "description": "",
            "help_text": "What to do with the tables",
        },
        "table name": {
            "default": "table1",
            "kind": "string",
            "default_units": "",
            "enumeration": tuple(),
            "format_string": "",
            "description": " table ",
            "help_text": "The name of the table.",
        },
        "columns": {
            "default": [],
            "kind": "list",
            "default_units": "",
            "enumeration": tuple(),
            "format_string": "",
            "description": "columns",
            "help_text": "The column definitions.",
        },
        "filename": {
            "default": "",
            "kind": "string",
            "default_units": "",
            "enumeration": tuple(),
            "format_string": "",
            "description": "File name:",
            "help_text": "The file name for the table, which may include a path.",
        },
        "file type": {
            "default": "from extension",
            "kind": "string",
            "default_units": "",
            "enumeration": (
                "from extension",
                ".csv",
                ".json",
                ".xlsx",
                ".txt",
            ),
            "format_string": "",
            "description": "File type:",
            "help_text": "The type of file to read/write.",
        },
        "frequency": {
            "default": 1,
            "kind": "integer",
            "default_units": "",
            "enumeration": tuple(),
            "format_string": "",
            "description": "Frequency:",
            "help_text": "Number of calls before saving the table.",
        },
        "index column": {
            "default": "--none--",
            "kind": "string",
            "default_units": "",
            "enumeration": tuple("--none--"),
            "format_string": "",
            "description": "Index column:",
            "help_text": "The column to index the table. Values must be unique.",
        },
        "row": {
            "default": "current",
            "kind": "string",
            "default_units": "",
            "enumeration": tuple("current"),
            "format_string": "",
            "description": "Row:",
            "help_text": "The row to access",
        },
        "column": {
            "default": "current",
            "kind": "string",
            "default_units": "",
            "enumeration": tuple("current"),
            "format_string": "",
            "description": "Column:",
            "help_text": "The column to access",
        },
        "value": {
            "default": "",
            "kind": "string",
            "default_units": "",
            "enumeration": tuple(),
            "format_string": "",
            "description": "Value:",
            "help_text": "The value to put into the table.",
        },
        "variable name": {
            "default": "",
            "kind": "string",
            "default_units": "",
            "enumeration": tuple(),
            "format_string": "",
            "description": "Variable name:",
            "help_text": (
                "The name of the variable for storing the value from the table."
            ),
        },
    }

    def __init__(self, defaults={}, data=None):
        """Initialize the instance, by default from the default
        parameters given in the class"""

        super().__init__(defaults={**TableParameters.parameters, **defaults}, data=data)
