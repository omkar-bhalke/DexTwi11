#!/usr/bin/env python3
"""Run from a source checkout or a packaged REA installation."""

from project.client import cli

if __name__ == "__main__":
    raise SystemExit(cli())
