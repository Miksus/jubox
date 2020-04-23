
import pytest

from jubox import JupyterNotebook, JupyterCell
from nbformat.notebooknode import NotebookNode

from nbformat.v4 import new_code_cell

def test_getitem():
    
    nb = JupyterNotebook([
        JupyterCell("first cell"),
        JupyterCell("second cell"),
        JupyterCell("third cell"),
    ])

    assert nb[0]["source"] == "first cell"
    assert nb[1]["source"] == "second cell"
    assert nb[2]["source"] == "third cell"

def test_getitem():

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
    
    nb = JupyterNotebook([
        JupyterCell("first cell"),
        JupyterCell("second cell"),
        JupyterCell("third cell"),
    ])

    nb[0] = JupyterCell("overwritten cell a")
    assert isinstance(nb[0], JupyterCell)
    assert nb[0]["source"] == "overwritten cell a"

    nb[1] = new_code_cell("overwritten cell b")
    assert isinstance(nb[0], JupyterCell)
    assert nb[1]["source"] == "overwritten cell b"

def test_setitem_slice():
    
    nb = JupyterNotebook([
        JupyterCell("first cell"),
        JupyterCell("second cell"),
        JupyterCell("third cell"),
    ])

    nb[0:2] = [JupyterCell("overwritten cell 1a"), JupyterCell("overwritten cell 2a")]
    assert isinstance(nb[0], JupyterCell)
    assert nb[0]["source"] == "overwritten cell 1a"
    assert nb[1]["source"] == "overwritten cell 2a"

    nb[0:2] = [new_code_cell("overwritten cell 1b"), new_code_cell("overwritten cell 2b")] 
    assert isinstance(nb[0], JupyterCell)
    assert nb[0]["source"] == "overwritten cell 1b"
    assert nb[1]["source"] == "overwritten cell 2b"

def test_delitem():
    
    nb = JupyterNotebook([
        JupyterCell("first cell"),
        JupyterCell("second cell"),
        JupyterCell("third cell"),
    ])

    del nb[1]
    assert nb[0]["source"] == "first cell"
    assert nb[1]["source"] == "third cell"
    assert 2 == len(nb.node.cells)

def test_delitem_slice():
    nb = JupyterNotebook([
        JupyterCell("first cell"),
        JupyterCell("second cell"),
        JupyterCell("third cell"),
    ])

    del nb[0:2]
    assert nb[0]["source"] == "third cell"
    assert 1 == len(nb.node.cells)


