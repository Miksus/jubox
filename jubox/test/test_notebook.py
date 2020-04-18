
import os
from pathlib import Path

import pytest

from jubox import JupyterNotebook

ROOT = os.path.dirname(__file__)

def test_creation_from_file():
    file = f"{ROOT}/test_files/nb_simple.ipynb"
    nb = JupyterNotebook(file)
    assert nb.file == file
    assert nb.node.cells[0].source == "# This is simple Jupyter Notebook"

def test_creation_from_pathlib_file():
    file = Path(ROOT) / "/test_files/nb_simple.ipynb"
    nb = JupyterNotebook(file)
    assert nb.file == file
    assert nb.node.cells[0].source == "# This is simple Jupyter Notebook"

def test_execute_inplace():
    file = f"{ROOT}/test_files/nb_unrun.ipynb"
    nb = JupyterNotebook(file)

    with pytest.raises(IndexError):
        # Should not have outputs thus error is raised
        nb.node.cells[-1].outputs[0]

    nb(inplace=True)

    assert nb.node.cells[-1].outputs[0]["data"]["text/plain"] == "'foobar'"

def test_execute_not_inplace():
    file = f"{ROOT}/test_files/nb_unrun.ipynb"
    nb = JupyterNotebook(file)

    with pytest.raises(IndexError):
        # Should not have outputs thus error is raised
        nb.node.cells[-1].outputs[0]

    nb_run = nb(inplace=False)

    assert nb_run.node.cells[-1].outputs[0]["data"]["text/plain"] == "'foobar'"

