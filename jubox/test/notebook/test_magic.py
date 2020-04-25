

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

