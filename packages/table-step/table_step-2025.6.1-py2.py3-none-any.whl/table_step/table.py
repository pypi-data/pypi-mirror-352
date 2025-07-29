# -*- coding: utf-8 -*-

"""Non-graphical part of the Table step in SEAMM"""

import logging
from pathlib import Path, PurePath

import numpy as np
import pandas
from tabulate import tabulate

import seamm
import seamm_util.printing as printing
from seamm_util import ureg, Q_, units_class  # noqa: F401
import table_step

logger = logging.getLogger(__name__)
job = printing.getPrinter()
printer = printing.getPrinter("table")


class Table(seamm.Node):
    def __init__(self, flowchart=None, extension=None):
        """Setup the non-graphical part of the Table step in SEAMM.

        Keyword arguments:
        """
        logger.debug("Creating Table {}".format(self))

        # Initialize our parent class
        super().__init__(
            flowchart=flowchart, title="Table", extension=extension, logger=logger
        )

        # This needs to be after initializing subclasses...
        self.parameters = table_step.TableParameters()
        self.calls = 0

    @property
    def version(self):
        """The semantic version of this module."""
        return table_step.__version__

    @property
    def git_revision(self):
        """The git version of this module."""
        return table_step.__git_revision__

    def description_text(self, P=None):
        """Return a short description of this step.

        Return a nicely formatted string describing what this step will
        do.

        Keyword arguments:
            P: a dictionary of parameter values, which may be variables
                or final values. If None, then the parameters values will
                be used as is.
        """

        if not P:
            P = self.parameters.values_to_dict()

        method = P["method"]
        tablename = P["table name"]
        lines = [self.header]
        lines.append(f"    {method} table '{tablename}'")

        if method == "Create":
            table = {"Column": [], "Type": [], "Default": []}
            for d in self.parameters["columns"].value:
                try:
                    table["Column"].append(self.get_value(d["name"]))
                except Exception:
                    table["Column"].append(d["name"])
                table["Type"].append(d["type"])
                if d["default"] == "":
                    table["Default"].append("")
                else:
                    try:
                        table["Default"].append(self.get_value(d["default"]))
                    except Exception:
                        table["Default"].append(d["default"])
            for tmp in tabulate(table, headers="keys", tablefmt="grid").splitlines():
                lines.append(8 * " " + tmp)
        elif method == "Read":
            filename = P["filename"]
            file_type = P["file type"]
            if file_type == "from extension":
                if isinstance(filename, str) and self.is_expr(filename):
                    lines.append(
                        f"        File: from variable '{filename}' with type from the "
                        "extension"
                    )
                else:
                    file_type = PurePath(filename).suffix
                    if file_type not in self.parameters["file type"].enumeration:
                        types = "', '".join(self.parameters["file type"].enumeration)
                        raise RuntimeError(
                            f"Cannot handle files of type '{file_type}' when reading "
                            f"table '{tablename}'.\nKnown types: '{types}'"
                        )
                    lines.append(
                        f"         File: '{filename}' with type '{file_type}' from the "
                        "extension."
                    )
            else:
                lines.append(f"         File: '{filename}' with type '{file_type}'")
        elif method == "Save":
            pass
        elif method == "Save as":
            filename = P["filename"]
            file_type = P["file type"]
            if file_type == "from extension":
                file_type = PurePath(filename).suffix
                if file_type not in self.parameters["file type"].enumeration:
                    types = "', '".join(self.parameters["file type"].enumeration)
                    raise RuntimeError(
                        f"Cannot handle files of type '{file_type}' when reading "
                        f"table '{tablename}'.\nKnown types: '{types}'"
                    )
                lines.append(
                    f"         File: '{filename}' with type '{file_type}' from the "
                    "extension."
                )
            else:
                lines.append(f"         File: '{filename}' with type '{file_type}'")
        elif method == "Print":
            pass
        elif method == "Print the current row of":
            pass
        elif method == "Append a row to":
            table = {"Column": [], "Value": []}
            for d in self.parameters["columns"].value:
                try:
                    table["Column"].append(self.get_value(d["name"]))
                except Exception:
                    table["Column"].append(d["name"])
                try:
                    table["Value"].append(self.get_value(d["value"]))
                except Exception:
                    table["Value"].append(d["value"])
            for tmp in tabulate(table, headers="keys", tablefmt="grid").splitlines():
                lines.append(8 * " " + tmp)
        elif method == "Go to the next row of":
            pass
        elif method == "Add columns to":
            table = {"Column": [], "Type": [], "Default": []}
            for d in self.parameters["columns"].value:
                try:
                    table["Column"].append(self.get_value(d["name"]))
                except Exception:
                    table["Column"].append(d["name"])
                table["Type"].append(d["type"])
                if d["type"] == "boolean":
                    if d["default"] == "":
                        default = False
                    else:
                        default = bool(d["default"])
                elif d["type"] == "integer":
                    if d["default"] == "":
                        default = 0
                    else:
                        default = int(d["default"])
                elif d["type"] == "float":
                    if d["default"] == "":
                        default = np.nan
                    else:
                        default = float(d["default"])
                elif d["type"] == "string":
                    default = d["default"]
                table["Default"].append(default)
            for tmp in tabulate(table, headers="keys", tablefmt="grid").splitlines():
                lines.append(8 * " " + tmp)
        elif method == "Get element of":
            if P["column"] == "":
                raise RuntimeError("Table get element: the column must be given")
            column = P["column"]
            if P["row"] == "":
                raise RuntimeError("Table get element: the row must be given")
            row = P["row"]
            lines.append(f"        row {row}, column {column}")
        elif method == "Set element of":
            if P["column"] == "":
                raise RuntimeError("Table set element: the column must be given")
            column = P["column"]
            if P["row"] == "":
                raise RuntimeError("Table set element: the row must be given")
            row = P["row"]
            value = P["value"]
            lines.append(f"        row {row}, column {column} = {value}")
        else:
            methods = ", ".join(table_step.methods)
            raise RuntimeError(
                f"The table method must be one of {methods}, not {method}."
            )

        return "\n".join(lines)

    def run(self):
        """Do what we need for the table, as dictated by the 'method'"""

        next_node = super().run(printer)
        # Get the values of the parameters, dereferencing any variables
        P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )
        tablename = P["table name"]

        # Pathnames are relative to current working directory
        wd = Path(self.directory).parent

        # Print out header to the main output
        printer.important(self.description_text(P))
        printer.important("")

        if P["method"] == "Create":
            table = pandas.DataFrame()
            defaults = {}
            for d in self.parameters["columns"].value:
                column_name = self.get_value(d["name"])
                if column_name not in table.columns:
                    if d["type"] == "boolean":
                        if d["default"] == "":
                            default = False
                        else:
                            default = bool(d["default"])
                    elif d["type"] == "integer":
                        if d["default"] == "":
                            default = 0
                        else:
                            default = int(d["default"])
                    elif d["type"] == "float":
                        if d["default"] == "":
                            default = np.nan
                        else:
                            default = float(d["default"])
                    elif d["type"] == "string":
                        default = d["default"]

                    table[column_name] = default
                    defaults[column_name] = default

            self.logger.info(f"Creating table '{tablename}'")

            index = P["index column"]
            if index == "" or index == "--none--":
                index = None
            else:
                if index not in table.columns:
                    columns = ", ".join(table.columns)
                    raise ValueError(
                        f"The index column '{index}' is not in the table: columns = "
                        f"{columns}"
                    )
                table.set_index(index, inplace=True)
            self.set_variable(
                tablename,
                {
                    "type": "pandas",
                    "table": table,
                    "defaults": defaults,
                    "index column": index,
                    "loop index": False,
                    "current index": 0,
                },
            )
        elif P["method"] == "Read":
            filename = P["filename"]

            self.logger.debug("  read table from {}".format(filename))

            file_type = P["file type"]
            if file_type == "from extension":
                file_type = PurePath(filename).suffix
                if file_type not in self.parameters["file type"].enumeration:
                    types = "', '".join(self.parameters["file type"].enumeration)
                    raise RuntimeError(
                        f"Cannot handle files of type '{file_type}' when reading "
                        f"table '{tablename}'.\nKnown types: '{types}'"
                    )

            if file_type == ".csv":
                table = pandas.read_csv(filename, index_col=False)
            elif file_type == ".json":
                table = pandas.read_json(filename)
            elif file_type == ".xlsx":
                table = pandas.read_excel(filename, index_col=False)
            elif file_type == ".txt":
                table = pandas.read_fwf(filename, index_col=False)
            else:
                types = "', '".join(self.parameters["file type"].enumeration)
                raise RuntimeError(
                    f"Table save: cannot handle format '{file_type}' for file "
                    f"'{filename}'\nKnown types: '{types}'"
                )

            index = P["index column"]
            if index == "" or index == "--none--":
                index = None
            else:
                if index not in table.columns:
                    columns = ", ".join(table.columns)
                    raise ValueError(
                        f"The index column '{index}' is not in the table: columns = "
                        f"{columns}"
                    )
                table.set_index(index, inplace=True)

            self.logger.debug("  setting up dict in {}".format(tablename))
            self.set_variable(
                tablename,
                {
                    "type": "pandas",
                    "filename": filename,
                    "table": table,
                    "defaults": {},
                    "index column": index,
                    "loop index": False,
                    "current index": 0,
                },
            )

            self.logger.info("Successfully read table from {}".format(filename))
        elif P["method"] == "Save" or P["method"] == "Save as":
            self.calls += 1
            if self.calls % P["frequency"] == 0:
                if not self.variable_exists(tablename):
                    raise RuntimeError(
                        "Table save: table '{}' does not exist.".format(tablename)
                    )
                file_type = P["file type"]
                table_handle = self.get_variable(tablename)
                table = table_handle["table"]

                if P["method"] == "Save as":
                    filename = P["filename"].strip()
                    if filename.startswith("/"):
                        filename = str(
                            Path(self.flowchart.root_directory) / filename[1:]
                        )
                    else:
                        filename = str(wd / filename)
                    table_handle["filename"] = filename
                else:
                    if "filename" not in table_handle:
                        if file_type == "from extension":
                            file_type = ".csv"
                        table_handle["filename"] = str(wd / tablename) + file_type
                    filename = table_handle["filename"]

                index = table_handle["index column"]

                if file_type == "from extension":
                    file_type = PurePath(filename).suffix
                    if file_type not in self.parameters["file type"].enumeration:
                        types = "', '".join(self.parameters["file type"].enumeration)
                        raise RuntimeError(
                            f"Cannot handle files of type '{file_type}' when writing "
                            f"table '{tablename}'.\nKnown types: '{types}'"
                        )
                if file_type == ".csv":
                    if index is None:
                        table.to_csv(filename, index=False)
                    else:
                        table.to_csv(filename, index=True, header=True)
                elif file_type == ".json":
                    if index is None:
                        table.to_json(filename, indent=4, orient="table", index=False)
                    else:
                        table.to_json(filename, indent=4, orient="table", index=True)
                elif file_type == ".xlsx":
                    if index is None:
                        table.to_excel(filename, index=False)
                    else:
                        table.to_excel(filename, index=True)
                elif file_type == ".txt":
                    with open(filename, "w") as fd:
                        if index is None:
                            fd.write(table.to_string(header=True, index=False))
                        else:
                            fd.write(table.to_string(header=True, index=True))
                else:
                    types = "', '".join(self.parameters["file type"].enumeration)
                    raise RuntimeError(
                        f"Table save: cannot handle format '{file_type}' for file "
                        f"'{filename}'\nKnown types: '{types}'"
                    )
        elif P["method"] == "Print":
            table_handle = self.get_variable(tablename)
            table = table_handle["table"]
            index = table_handle["index column"]
            if index is None:
                text = table.to_string(header=True, index=False)
            else:
                text = table.to_string(header=True, index=True)

            for line in text.splitlines():
                printer.normal(4 * " " + line)
            printer.normal("")

        elif P["method"] == "Print the current row of":
            table_handle = self.get_variable(tablename)
            table = table_handle["table"]
            index = table_handle["current index"]
            self.logger.debug("index = {}".format(index))
            index = table.index.get_loc(index)
            self.logger.debug("  --> {}".format(index))
            if index is None:
                lines = table.to_string(header=True, index=False)
            else:
                lines = table.to_string(header=True, index=True)

            self.logger.debug(lines)
            self.logger.debug("-----")

            if index == 0:
                printer.normal("\n    Table '{}':".format(tablename))
                printer.normal("\n    ".join(lines.splitlines()[0:2]))
            else:
                printer.normal(4 * " " + lines.splitlines()[index + 1])

        elif P["method"] == "Append a row to":
            if not self.variable_exists(tablename):
                raise RuntimeError(
                    "Table save: table '{}' does not exist.".format(tablename)
                )
            table_handle = self.get_variable(tablename)
            if "defaults" in table_handle:
                defaults = table_handle["defaults"]
            else:
                defaults = {}
            table = table_handle["table"]
            column_types = {}
            for column_name, column_type in zip(table.columns, table.dtypes):
                if column_type == "object":
                    column_types[column_name] = "string"
                elif column_type == "bool":
                    column_types[column_name] = "boolean"
                elif column_type == "int64":
                    column_types[column_name] = "integer"
                elif column_type == "float64":
                    column_types[column_name] = "float"

            new_row = {}

            for d in self.parameters["columns"].value:
                column_name = self.get_value(d["name"])
                value = self.get_value(d["value"])
                column_type = column_types[column_name]
                if value == "default":
                    if column_name in defaults:
                        value = defaults[column_name]
                    else:
                        if column_type == "boolean":
                            value = False
                        elif column_type == "integer":
                            value = 0
                        elif column_type == "float":
                            value = np.nan
                        elif column_type == "string":
                            value = ""
                new_row[column_name] = [value]
            new_row = pandas.DataFrame.from_dict(new_row)
            table = pandas.concat([table, new_row], ignore_index=True)
            seamm.flowchart_variables[tablename]["table"] = table
            seamm.flowchart_variables[tablename]["current index"] = table.shape[0] - 1
        elif P["method"] == "Go to the next row of":
            if not self.variable_exists(tablename):
                raise RuntimeError(
                    "Table save: table '{}' does not exist.".format(tablename)
                )
            table_handle = self.get_variable(tablename)
            table_handle["current index"] += 1

        elif P["method"] == "Add columns to":
            if not self.variable_exists(tablename):
                raise RuntimeError(
                    "Table save: table '{}' does not exist.".format(tablename)
                )
            table_handle = self.get_variable(tablename)
            table = table_handle["table"]
            for d in self.parameters["columns"].value:
                column_name = self.get_value(d["name"])
                if column_name in table.columns:
                    # Need to check if this is an error
                    pass
                else:
                    if d["type"] == "boolean":
                        if d["default"] == "":
                            default = False
                        else:
                            default = bool(d["default"])
                    elif d["type"] == "integer":
                        if d["default"] == "":
                            default = 0
                        else:
                            default = int(d["default"])
                    elif d["type"] == "float":
                        if d["default"] == "":
                            default = np.nan
                        else:
                            default = float(d["default"])
                    elif d["type"] == "string":
                        default = d["default"]
                    table[d["name"]] = default
        elif P["method"] == "Get element of":
            if not self.variable_exists(tablename):
                raise RuntimeError(
                    "Table get element: table '{}' does not exist.".format(tablename)
                )
            if P["column"] == "":
                raise RuntimeError("Table get element: the column must be given")
            column = self.get_value(P["column"])
            if P["row"] == "":
                raise RuntimeError("Table get element: the row must be given")
            row = self.get_value(P["row"])
            if P["variable name"] == "":
                raise RuntimeError(
                    "Table get element: the name of the variable to "
                    "set to the value must be given"
                )
            variable_name = self.get_value(P["variable name"])

            table_handle = self.get_variable(tablename)
            index = table_handle["index column"]
            table = table_handle["table"]

            if row == "current":
                row = table_handle["current index"]
            else:
                if index is None:
                    row = int(row)
                else:
                    if table.index.dtype.kind == "i":
                        row = int(row)
                    row = table.index.get_loc(int(row))
            try:
                column = int(column)
            except Exception:
                column = table.columns.get_loc(column)

            value = table.iat[row, column]
            self.set_variable(variable_name, value)
        elif P["method"] == "Set element of":
            if not self.variable_exists(tablename):
                raise RuntimeError(
                    "Table get element: table '{}' does not exist.".format(tablename)
                )
            if P["column"] == "":
                raise RuntimeError("Table get element: the column must be given")
            column = self.get_value(P["column"])
            if P["row"] == "":
                raise RuntimeError("Table get element: the row must be given")
            row = self.get_value(P["row"])
            if P["value"] == "":
                raise RuntimeError("Table set element: the value must be given")
            value = self.get_value(P["value"])

            table_handle = self.get_variable(tablename)
            index = table_handle["index column"]
            table = table_handle["table"]

            if row == "current":
                row = table_handle["current index"]
            else:
                if index is None:
                    row = int(row)
                else:
                    if table.index.dtype.kind == "i":
                        row = int(row)
                    row = table.index.get_loc(row)
            try:
                column = int(column)
            except Exception:
                column = table.columns.get_loc(column)

            table.iat[row, column] = value
        else:
            methods = ", ".join(table_step.methods)
            raise RuntimeError(
                f"The table method must be one of {methods}, not {P['method']}."
            )

        return next_node
