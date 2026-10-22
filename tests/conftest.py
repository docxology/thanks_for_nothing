# Copyright (c) 2026 Daniel Ari Friedman
"""Register shared fixtures without importing collected test modules."""

pytest_plugins = ("tests.support.pipeline", "tests.support.fixtures")
