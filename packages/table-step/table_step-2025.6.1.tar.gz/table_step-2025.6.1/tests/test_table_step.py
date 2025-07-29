#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `table_step` package."""

import pytest  # noqa: F401
import table_step  # noqa: F401


def test_construction():
    """Simplest test that we can make a Table object"""
    table = table_step.Table()
    assert str(type(table)) == "<class 'table_step.table.Table'>"
