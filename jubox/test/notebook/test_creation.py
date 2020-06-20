import os
from pathlib import Path

import pytest

from jubox import JupyterNotebook, CodeCell
from nbformat.notebooknode import NotebookNode

def test_creation_from_file(notebook_file_simple):
    #file = f"{notebook_folder}/nb_simple.ipynb"
    file = notebook_file_simple
    nb = JupyterNotebook(file)
    assert nb.file == file
    assert isinstance(nb.node, NotebookNode)
    assert nb.node.cells[0].source == "# This is simple Jupyter Notebook"

def test_creation_from_pathlib_file(notebook_file_simple):
    file = Path(notebook_file_simple)
    nb = JupyterNotebook(file)
    assert nb.file == file
    assert isinstance(nb.node, NotebookNode)
    assert nb.node.cells[0].source == "# This is simple Jupyter Notebook"

def test_creation_empty():
    nb = JupyterNotebook()
    assert isinstance(nb.node, NotebookNode)

def test_creation_list_of_cells():
    nb = JupyterNotebook([
        CodeCell("1 cell"),
        CodeCell("2 cell"),
        CodeCell("3 cell"),
    ])
    assert isinstance(nb.node, NotebookNode)
    assert len(nb.node.cells) == 3
    assert isinstance(nb.node.cells[0], NotebookNode)

    assert "1 cell" == nb.node.cells[0]["source"]
    assert "2 cell" == nb.node.cells[1]["source"]
    assert "3 cell" == nb.node.cells[2]["source"]

def test_creation_list_of_empty_cells():
    nb = JupyterNotebook([
        CodeCell(),
        CodeCell(),
        CodeCell(),
    ])
    assert isinstance(nb.node, NotebookNode)
    assert len(nb.node.cells) == 3
    assert isinstance(nb.node.cells[0], NotebookNode)

def test_creation_another_notebook():
    nb_orig = JupyterNotebook([
        CodeCell("1 cell"),
        CodeCell("2 cell"),
        CodeCell("3 cell"),
    ])

    nb = JupyterNotebook(nb_orig)

    assert isinstance(nb.node, NotebookNode)
    assert len(nb.node.cells) == 3
    assert isinstance(nb.node.cells[0], NotebookNode)

    assert nb.node is nb_orig.node