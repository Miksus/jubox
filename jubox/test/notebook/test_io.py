
import pytest

from jubox import JupyterNotebook, JupyterCell, RawCell
from nbformat.notebooknode import NotebookNode

from nbformat.v4 import new_code_cell

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

def test_to_html(notebook_path):
    html_path = notebook_path.parent / "file.html"
    html_path = str(html_path)

    nb = JupyterNotebook(notebook_path)
    nb.to_html(html_path)

    with open(html_path) as file:
        cont = file.read()
    assert "# This is simple Jupyter Notebook" in cont
    assert "<!DOCTYPE html" in cont

def test_to_html_path(notebook_path):
    html_path = notebook_path.parent / "file.html"

    nb = JupyterNotebook(notebook_path)
    nb.to_html(html_path)

    with open(html_path) as file:
        cont = file.read()
    assert "# This is simple Jupyter Notebook" in cont
    assert "<!DOCTYPE html" in cont

def test_to_ipynb(notebook_path):
    ipynb_path = notebook_path.parent / "file.ipynb"
    ipynb_path = str(ipynb_path)

    nb = JupyterNotebook(notebook_path)
    nb.to_ipynb(ipynb_path)

    with open(ipynb_path) as file:
        cont = file.read()
    assert "# This is simple Jupyter Notebook" in cont
    assert '"nbformat":' in cont # Check it has Notebooks' autogenerated stuff

def test_to_ipynb_path(notebook_path):
    ipynb_path = notebook_path.parent / "file.ipynb"

    nb = JupyterNotebook(notebook_path)
    nb.to_ipynb(ipynb_path)

    with open(ipynb_path) as file:
        cont = file.read()
    assert "# This is simple Jupyter Notebook" in cont
    assert '"nbformat":' in cont # Check it has Notebooks' autogenerated stuff
