
import os
from pathlib import Path

import pytest

from jubox import JupyterNotebook, JupyterCell

ROOT = os.path.dirname(__file__)

def test_execute_inplace(notebook_folder):
    file = f"{notebook_folder}/nb_unrun.ipynb"
    nb = JupyterNotebook(file)

    with pytest.raises(IndexError):
        # Should not have outputs thus error is raised
        nb.node.cells[-1].outputs[0]

    nb(inplace=True)

    assert nb.node.cells[-1].outputs[0]["data"]["text/plain"] == "'foobar'"

def test_execute_not_inplace(notebook_folder):
    file = f"{notebook_folder}/nb_unrun.ipynb"
    nb = JupyterNotebook(file)

    with pytest.raises(IndexError):
        # Should not have outputs thus error is raised
        nb.node.cells[-1].outputs[0]

    nb_run = nb(inplace=False)

    assert nb_run.node.cells[-1].outputs[0]["data"]["text/plain"] == "'foobar'"
