
import pytest

from jubox import JupyterNotebook, JupyterCell
from nbformat.notebooknode import NotebookNode

from nbformat.v4 import new_code_cell

def test_getitem():
    #file = f"{notebook_folder}/nb_simple.ipynb"
    nb = JupyterNotebook([
        JupyterCell("first cell"),
        JupyterCell("second cell"),
        JupyterCell("third cell"),
    ])

    assert nb[0]["source"] == "first cell"
    assert nb[1]["source"] == "second cell"
    assert nb[2]["source"] == "third cell"

def test_getitem():
    #file = f"{notebook_folder}/nb_simple.ipynb"
    nb = JupyterNotebook([
        JupyterCell("first cell"),
        JupyterCell("second cell"),
        JupyterCell("third cell"),
    ])

    assert isinstance(nb[0], JupyterCell)
    assert isinstance(nb[1], JupyterCell)
    assert isinstance(nb[2], JupyterCell)

    assert nb[0]["source"] == "first cell"
    assert nb[1]["source"] == "second cell"
    assert nb[2]["source"] == "third cell"

def test_setitem():
    #file = f"{notebook_folder}/nb_simple.ipynb"
    nb = JupyterNotebook([
        JupyterCell("first cell"),
        JupyterCell("second cell"),
        JupyterCell("third cell"),
    ])

    nb[0] = JupyterCell("overwritten cell")
    assert isinstance(nb[0], JupyterCell)
    assert nb[0]["source"] == "overwritten cell"

    nb[1] = new_code_cell("overwritten cell")
    assert isinstance(nb[0], JupyterCell)
    assert nb[1]["source"] == "overwritten cell"

def test_iter():
    #file = f"{notebook_folder}/nb_simple.ipynb"
    nb = JupyterNotebook([
        JupyterCell("1 cell"),
        JupyterCell("2 cell"),
        JupyterCell("3 cell"),
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
