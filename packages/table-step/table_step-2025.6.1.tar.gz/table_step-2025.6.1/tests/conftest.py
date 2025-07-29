#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Fixtures for testing the table_step package."""

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--no-unit", action="store_true", default=False, help="don't run the unit tests"
    )
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run the integration tests",
    )
    parser.addoption(
        "--timing", action="store_true", default=False, help="run the timing tests"
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "unit: unit tests run by default, use '--no-unit' to turn off"
    )
    config.addinivalue_line(
        "markers", "integration: integration test, run with --integration"
    )
    config.addinivalue_line("markers", "timing: timing tests, run with --timing")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--no-unit"):
        skip = pytest.mark.skip(reason="remove --no-unit option to run")
        for item in items:
            if "unit" in item.keywords:
                item.add_marker(skip)
    if not config.getoption("--integration"):
        skip = pytest.mark.skip(reason="use the --integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip)
    if not config.getoption("--timing"):
        skip = pytest.mark.skip(reason="need --timing option to run")
        for item in items:
            if "timing" in item.keywords:
                item.add_marker(skip)
