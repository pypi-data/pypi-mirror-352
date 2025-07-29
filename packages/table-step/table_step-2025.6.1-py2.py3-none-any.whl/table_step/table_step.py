# -*- coding: utf-8 -*-

"""Helper class needed for the stevedore integration.

This must provide a description() method that returns a dict containing a
description of this node, and create_node() and create_tk_node() methods for
creating the graphical and non-graphical nodes.

"""

import table_step


class TableStep(object):
    my_description = {
        "description": "An interface for Pandas tables",
        "group": "Data",
        "name": "Table",
    }
    """The description needs three fields:

    description:
        A human-readable description of this step. It can be
        several lines long, and needs to be clear to non-expert users.
    group:
        Which group in the menus to put this step. If the group does
        not exist it will be created. Common groups are 'Building',
        'Calculations', 'Control' and 'Data'.
    name:
        The name of this step, to be displayed in the menus.

    """

    def __init__(self, flowchart=None, gui=None):
        """Initialize this helper class, which is used by
        the application via stevedore to get information about
        and create node objects for the flowchart
        """
        pass

    def description(self):
        """Return a description of what this extension does"""
        return TableStep.my_description

    def create_node(self, flowchart=None, **kwargs):
        """Return the new node object"""
        return table_step.Table(flowchart=flowchart, **kwargs)

    def create_tk_node(self, canvas=None, **kwargs):
        """Return the graphical Tk node object"""
        return table_step.TkTable(canvas=canvas, **kwargs)
