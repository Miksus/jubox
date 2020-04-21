
from jubox import JupyterCell
from nbformat.notebooknode import NotebookNode

def test_append():
    cell = JupyterCell("foo string")
    cell.append(" bar string")
    assert cell.data["source"] == "foo string bar string"

def test_insert():
    cell = JupyterCell("foo string")
    cell.insert(3, " bar")
    assert cell.data["source"] == "foo bar string"
