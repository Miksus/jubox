

import pytest

from jubox import JupyterNotebook, JupyterCell, RawCell
from nbformat.notebooknode import NotebookNode

from nbformat.v4 import new_code_cell

def test_iter():
    
    nb = JupyterNotebook([
        RawCell("1 cell"),
        RawCell("2 cell"),
        RawCell("3 cell"),
    ])

    for i, cell in enumerate(nb):
        assert isinstance(cell, JupyterCell)
        assert cell["source"] == "{} cell".format(i+1)

def test_with(notebook_file_unrun):
    nb = JupyterNotebook(notebook_file_unrun)
    assert 'print("This notebook is not run")' == nb.node.cells[0]["source"]
    with nb:
        nb.node.cells[0]["source"] = 'print("This notebook is modified")'
        assert 'print("This notebook is modified")' == nb.node.cells[0]["source"]

    # Loading the notebook again to check the changes are still there 
    # (with statement should save when exiting)
    nb_reloaded = JupyterNotebook(notebook_file_unrun)
    assert 'print("This notebook is modified")' == nb_reloaded.node.cells[0]["source"]