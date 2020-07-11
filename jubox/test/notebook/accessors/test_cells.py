import pytest

from jubox import JupyterNotebook, RawCell, CodeCell, MarkdownCell



import pytest

from jubox import JupyterNotebook, CodeCell, RawCell
from nbformat.notebooknode import NotebookNode

from nbformat.v4 import new_code_cell


def test_getitem():

    nb = JupyterNotebook([
        RawCell("first cell"),
        RawCell("second cell"),
        RawCell("third cell"),
    ])
    first_cell = nb.cells[0]
    sencond_cell = nb.cells[1]
    third_cell = nb.cells[2]
    assert first_cell["source"] == "first cell"
    assert sencond_cell["source"] == "second cell"
    assert third_cell["source"] == "third cell"

    first_cell, sencond_cell = nb.cells[0:2]
    assert first_cell["source"] == "first cell"
    assert sencond_cell["source"] == "second cell"

    first_cell, third_cell = nb.cells[[0, 2]]
    assert first_cell["source"] == "first cell"
    assert third_cell["source"] == "third cell"

def test_setitem():
    
    nb = JupyterNotebook([
        RawCell("first cell"),
        RawCell("second cell"),
        RawCell("third cell"),
    ])

    nb.cells[0] = RawCell("overwritten cell a")
    assert isinstance(nb.cells[0], RawCell)
    assert nb.cells[0]["source"] == "overwritten cell a"

    nb.cells[1] = new_code_cell("overwritten cell b")
    assert isinstance(nb.cells[1], CodeCell)
    assert nb.cells[1]["source"] == "overwritten cell b"

def test_setitem_slice():
    
    nb = JupyterNotebook([
        RawCell("first cell"),
        RawCell("second cell"),
        RawCell("third cell"),
    ])

    nb.cells[0:2] = [RawCell("overwritten cell 1a"), RawCell("overwritten cell 2a")]
    assert isinstance(nb[0], RawCell)
    assert nb[0]["source"] == "overwritten cell 1a"
    assert nb[1]["source"] == "overwritten cell 2a"

    nb.cells[0:2] = [new_code_cell("overwritten cell 1b"), new_code_cell("overwritten cell 2b")] 
    assert isinstance(nb[0], CodeCell)
    assert nb[0]["source"] == "overwritten cell 1b"
    assert nb[1]["source"] == "overwritten cell 2b"

def test_delitem():
    
    nb = JupyterNotebook([
        RawCell("first cell"),
        RawCell("second cell"),
        RawCell("third cell"),
    ])

    del nb.cells[1]
    assert nb.cells[0]["source"] == "first cell"
    assert nb.cells[1]["source"] == "third cell"
    assert 2 == len(nb.node.cells)

def test_delitem_slice():
    nb = JupyterNotebook([
        RawCell("first cell"),
        RawCell("second cell"),
        RawCell("third cell"),
    ])

    del nb.cells[0:2]
    assert nb.cells[0]["source"] == "third cell"
    assert 1 == len(nb.node.cells)

def test_len():
    nb = JupyterNotebook([
        RawCell("first cell"),
        RawCell("second cell"),
        RawCell("third cell"),
    ])
    assert 3 == len(nb.cells)

def test_reversed():
    nb = JupyterNotebook([
        RawCell("first cell"),
        RawCell("second cell"),
        RawCell("third cell"),
    ])
    nb_2 = reversed(nb.cells)
    assert "third cell" == nb_2.node.cells[0]["source"]
    assert "second cell" == nb_2.node.cells[1]["source"]
    assert "first cell" == nb_2.node.cells[2]["source"]

    assert "first cell" == nb.node.cells[0]["source"]
    assert "second cell" == nb.node.cells[1]["source"]
    assert "third cell" == nb.node.cells[2]["source"]