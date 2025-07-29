# -*- coding: utf-8 -*-

"""The graphical part of a Table step"""

import copy
import logging
import pprint  # noqa: F401
import tkinter as tk
import tkinter.ttk as ttk

import seamm
import seamm_widgets as sw
import table_step

logger = logging.getLogger(__name__)


class TkTable(seamm.TkNode):
    """The node_class is the class of the 'real' node that this
    class is the Tk graphics partner for
    """

    node_class = table_step.Table

    def __init__(
        self,
        tk_flowchart=None,
        node=None,
        canvas=None,
        x=120,
        y=20,
        w=200,
        h=50,
        my_logger=logger,
    ):
        """Initialize a node

        Keyword arguments:
        """
        self._columns = {}

        super().__init__(
            tk_flowchart=tk_flowchart,
            node=node,
            node_type="table",
            canvas=canvas,
            x=x,
            y=y,
            w=w,
            h=h,
            my_logger=my_logger,
        )

    def create_dialog(self):
        """Create the dialog!"""
        frame = super().create_dialog(title="Edit Table Step")

        # Create the widgets and grid them in
        P = self.node.parameters
        for key in P:
            if key != "columns":
                self[key] = P[key].widget(frame)

        self._columns = copy.deepcopy(self.node.parameters["columns"].value)

        # area for columns
        self["columns"] = ttk.Frame(frame, height=300)

        self.reset_dialog()

        self["method"].bind("<<ComboboxSelected>>", self.reset_dialog)

    def reset_dialog(self, widget=None):
        """Layout the dialog based on the current values"""

        frame = self["frame"]

        # Remove any sizing info
        columns, rows = frame.grid_size()
        for column in range(columns):
            frame.columnconfigure(column, weight=0, minsize=0)
        for row in range(rows):
            frame.rowconfigure(row, weight=0, minsize=0)

        # Remove any widgets previously packed
        for slave in frame.grid_slaves():
            slave.grid_forget()

        # and get the method, which in this example controls
        # how the widgets are laid out.
        method = self["method"].get()

        # keep track of the row in a variable, so that the layout is flexible
        # if e.g. rows are skipped to control such as 'method' here
        row = 0
        self["method"].grid(row=row, column=0, columnspan=2, sticky=tk.EW)
        self["table name"].grid(row=row, column=2, sticky=tk.EW)
        row += 1

        if method == "Create":
            self["columns"].grid(row=row, column=0, columnspan=5, sticky=tk.NSEW)
            frame.rowconfigure(row, weight=1)
            frame.columnconfigure(5, weight=1)
            self.layout_columns(first=True)
            row += 1
            self["index column"].grid(row=row, column=0, columnspan=2, sticky=tk.EW)
            row += 1
        elif method == "Read":
            self["filename"].grid(row=row, column=1, columnspan=2, sticky=tk.EW)
            row += 1
            self["file type"].grid(row=row, column=1, columnspan=2, sticky=tk.EW)
            row += 1
            self["index column"].grid(row=row, column=1, columnspan=2, sticky=tk.EW)
            row += 1
            sw.align_labels([self["filename"], self["file type"], self["index column"]])
        elif method == "Save":
            self["file type"].grid(row=row, column=1, sticky=tk.EW)
            row += 1
            self["frequency"].grid(row=row, column=1, sticky=tk.EW)
            row += 1
            sw.align_labels([self["filename"], self["frequency"]])
        elif method == "Save as":
            self["filename"].grid(row=row, column=1, sticky=tk.EW)
            row += 1
            self["file type"].grid(row=row, column=1, sticky=tk.EW)
            row += 1
            self["frequency"].grid(row=row, column=1, sticky=tk.EW)
            row += 1
            sw.align_labels([self["filename"], self["file type"], self["frequency"]])
        elif method == "Print":
            pass
        elif method == "Print the current row of":
            pass
        elif method == "Append a row to":
            self["columns"].grid(row=row, column=0, columnspan=4, sticky=tk.NSEW)
            frame.rowconfigure(row, weight=1)
            frame.columnconfigure(4, weight=1)
            row += 1
            self.layout_columns_for_add_row(first=True)
        elif method == "Go to the next row of":
            pass
        elif method == "Add columns to":
            self["columns"].grid(row=row, column=0, columnspan=4, sticky=tk.NSEW)
            row += 1
            self.layout_columns(first=True)
        elif method == "Get element of":
            self["row"].grid(row=row, column=1, columnspan=2, sticky=tk.EW)
            row += 1
            self["column"].grid(row=row, column=1, columnspan=2, sticky=tk.EW)
            row += 1
            self["variable name"].grid(row=row, column=1, columnspan=2, sticky=tk.EW)
            row += 1
            sw.align_labels([self["row"], self["column"], self["variable name"]])
        elif method == "Set element of":
            self["row"].grid(row=row, column=1, columnspan=2, sticky=tk.EW)
            row += 1
            self["column"].grid(row=row, column=1, columnspan=2, sticky=tk.EW)
            row += 1
            self["value"].grid(row=row, column=1, columnspan=2, sticky=tk.EW)
            row += 1
            sw.align_labels([self["row"], self["column"], self["value"]])
        else:
            methods = ", ".join(self.parameters["method"].enumeration)
            raise RuntimeError(
                f"The table method must be one of {methods}, not '{method}'."
            )
        row += 1

        frame.columnconfigure(0, minsize=50)

        return row

    def right_click(self, event):
        """Probably need to add our dialog..."""

        super().right_click(event)
        self.popup_menu.add_command(label="Edit...", command=self.edit)

        self.popup_menu.tk_popup(event.x_root, event.y_root, 0)

    def handle_dialog(self, result):
        if result is None or result == "Cancel":
            self.dialog.deactivate(result)
            return

        if result == "Help":
            # display help!!!
            return

        if result != "OK":
            self.dialog.deactivate(result)
            raise RuntimeError("Don't recognize dialog result '{}'".format(result))

        super().handle_dialog(result)

        # and get the method, which in this example tells
        # whether to use the value directly or get it from
        # a variable in the flowchart

        method = self["method"].get()

        if method == "Create":
            tablename = self["table name"].get()
            self.node.tables = [tablename]
            self.save_column_data()
            self.node.parameters["columns"].value = copy.deepcopy(self._columns)
        elif method == "Read":
            tablename = self["table name"].get()
            self.node.tables = [tablename]
            pass
        elif method == "Save":
            pass
        elif method == "Save as":
            pass
        elif method == "Print":
            pass
        elif method == "Print the current row of":
            pass
        elif method == "Append a row to":
            self.save_column_data()
            self.node.parameters["columns"].value = copy.deepcopy(self._columns)
        elif method == "Go to the next row of":
            pass
        elif method == "Add columns to":
            # Save any changes!
            self.save_column_data()
            self.node.parameters["columns"].value = copy.deepcopy(self._columns)
        elif method == "Get element of":
            pass
        elif method == "Set element of":
            pass
        else:
            methods = ", ".join(self.parameters["method"].enumeration)
            raise RuntimeError(
                f"The table method must be one of {methods}, not '{method}'."
            )

    def layout_columns(self, first=False):
        """Layout the table of columns for adding, editing, etc."""

        frame = self["columns"]

        # Save any changes!
        if not first:
            self.save_column_data()

        # Unpack any widgets
        for slave in frame.grid_slaves():
            slave.destroy()

        row = 0
        w = ttk.Label(frame, text="Name", width=30)
        w.grid(row=row, column=1)
        w = ttk.Label(frame, text="Type", width=30)
        w.grid(row=row, column=2)
        w = ttk.Label(frame, text="Default", width=30)
        w.grid(row=row, column=3)

        for d in self._columns:
            row += 1
            widgets = d["widgets"] = {}

            col = 0
            # The button to remove a row...
            w = ttk.Button(
                frame,
                text="-",
                width=5,
                command=lambda row=row: self.remove_column(row - 1),
                takefocus=False,
            )
            w.grid(row=row, column=col, sticky=tk.W)
            col += 1
            widgets["remove"] = w

            # the name of the keyword
            w = ttk.Entry(
                frame,
                width=30,
                takefocus=False,
            )
            w.insert(0, d["name"])
            widgets["name"] = w
            w.grid(row=row, column=col, stick=tk.EW)
            col += 1

            # the type of the column
            w = ttk.Combobox(
                frame,
                state="readonly",
                values=("string", "boolean", "integer", "float"),
            )
            if "type" not in d:
                d["type"] = "float"
            w.set(d["type"])
            w.grid(row=row, column=col, stick=tk.EW)
            col += 1
            widgets["type"] = w

            # the default
            w = ttk.Entry(
                frame,
                width=30,
                takefocus=False,
            )
            w.insert(0, d["default"])
            widgets["default"] = w
            w.grid(row=row, column=col, stick=tk.EW)
            col += 1

        # The button to add a row...
        row += 1
        w = ttk.Button(
            frame,
            text="+",
            width=5,
            command=self.add_column,
            takefocus=False,
        )
        w.grid(row=row, column=0, sticky=tk.W)

    def layout_columns_for_add_row(self, first=False):
        """Layout the table of columns for adding a row"""

        frame = self["columns"]

        # Save any changes!
        if not first:
            self.save_column_data()

        # Unpack any widgets
        for slave in frame.grid_slaves():
            slave.destroy()

        row = 0
        w = ttk.Label(frame, text="Name")
        w.grid(row=row, column=1)
        w = ttk.Label(frame, text="Value")
        w.grid(row=row, column=2)

        for d in self._columns:
            row += 1
            widgets = d["widgets"] = {}

            col = 0
            # The button to remove a row...
            w = ttk.Button(
                frame,
                text="-",
                width=5,
                command=lambda row=row: self.remove_column_for_add_row(row - 1),
                takefocus=False,
            )
            w.grid(row=row, column=col, sticky=tk.W)
            col += 1
            widgets["remove"] = w

            # the name of the column
            w = ttk.Entry(
                frame,
                width=30,
                takefocus=False,
            )
            w.insert(0, d["name"])
            widgets["name"] = w
            w.grid(row=row, column=col, stick=tk.EW)
            col += 1

            # the value
            w = ttk.Entry(
                frame,
                width=30,
                takefocus=False,
            )
            w.insert(0, d["value"])
            widgets["value"] = w
            w.grid(row=row, column=col, stick=tk.EW)
            col += 1

        # The button to add a row...
        row += 1
        w = ttk.Button(
            frame,
            text="+",
            width=5,
            command=self.add_column_for_add_row,
            takefocus=False,
        )
        w.grid(row=row, column=0, sticky=tk.W)

    def remove_column(self, row=None):
        """Remove a column from the list of columns"""
        if row < len(self._columns):
            del self._columns[row]
        self.layout_columns()

    def add_column(self):
        """Add entries for another column in the displayed table"""
        self._columns.append(
            {"widgets": {}, "type": "float", "name": "", "default": ""}
        )
        self.layout_columns()

    def remove_column_for_add_row(self, row=None):
        """Remove a column from the list of columns"""
        if row < len(self._columns):
            del self._columns[row]
        self.layout_columns_for_add_row()

    def add_column_for_add_row(self):
        """Add entries for another column in the displayed table"""
        self._columns.append({"widgets": {}, "name": "", "value": ""})
        self.layout_columns_for_add_row()

    def save_column_data(self):
        """Get the data from the widgets when the table information is
        changed in the GUI.
        """
        for d in self._columns:
            w = d["widgets"]
            if "name" in w:
                d["name"] = w["name"].get()
            if "type" in w:
                d["type"] = w["type"].get()
            if "default" in w:
                d["default"] = w["default"].get()
            if "value" in w:
                d["value"] = w["value"].get()
            for name in w:
                w[name].destroy()
            del d["widgets"]
