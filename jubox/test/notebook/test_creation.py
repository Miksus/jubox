import os
from pathlib import Path

import pytest

from jubox import JupyterNotebook, JupyterCell
from nbformat.notebooknode import NotebookNode

def test_creation_from_file(notebook_file_simple):
    #file = f"{notebook_folder}/nb_simple.ipynb"
    file = notebook_file_simple
    nb = JupyterNotebook(file)
    assert nb.file == file
    assert isinstance(nb.node, NotebookNode)
    assert nb.node.cells[0].source == "# This is simple Jupyter Notebook"

def test_creation_from_pathlib_file(notebook_folder):
    file = Path(notebook_folder) / "/nb_simple.ipynb"
    nb = JupyterNotebook(file)
    assert nb.file == file
    assert isinstance(nb.node, NotebookNode)
    assert nb.node.cells[0].source == "# This is simple Jupyter Notebook"

def test_creation_empty():
    nb = JupyterNotebook()
    assert isinstance(nb.node, NotebookNode)

def test_creation_list_of_cells():
    nb = JupyterNotebook([
        JupyterCell(),
        JupyterCell(),
        JupyterCell(),
    ])
    assert isinstance(nb.node, NotebookNode)
    assert len(nb.node.cells) == 3
    assert isinstance(nb.node.cells[0], NotebookNode)