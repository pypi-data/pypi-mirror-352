"""Nox sessions."""

import os
import shlex
import shutil
import sys
from pathlib import Path
from textwrap import dedent

import nox

package = "tissue_properties/"
python_versions = ["3.10", "3.12"]
nox.needs_version = ">= 2021.6.6"
nox.options.sessions = ("tests",)


@nox.session(python=python_versions)
def tests(session) -> None:
    """Run the test suite."""
    session.install(".")
    session.install("pytest")
    session.run("pytest", *session.posargs)
