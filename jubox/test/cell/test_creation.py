
from jubox import JupyterCell
from nbformat.notebooknode import NotebookNode

from nbformat.v4 import new_code_cell, new_output

def test_initiation():
    cell = JupyterCell("x = 5")
    assert isinstance(cell.to_dict(), NotebookNode)
    assert cell.data.source == "x = 5"

def test_initiation_with_type():
    cell = JupyterCell("x = 5", cell_type="raw")
    assert isinstance(cell.to_dict(), NotebookNode)
    assert cell.data.source == "x = 5"
    assert cell.data.cell_type == "raw"

def test_initiation_with_tag():
    cell = JupyterCell("x = 5", tags=["tagged"])
    assert isinstance(cell.to_dict(), NotebookNode)
    assert cell.data.source == "x = 5"
    assert ["tagged"] == cell.data["metadata"]["tags"]

def test_initiation_empty():
    cell = JupyterCell()
    assert isinstance(cell.to_dict(), NotebookNode)

def test_initiation_from_node():
    node = new_code_cell("this is a cell", execution_count=2, outputs=[new_output("execute_result", data={"text/plain": "this is an output"})])
    cell = JupyterCell(node)

    assert isinstance(cell.to_dict(), NotebookNode)
    assert "this is a cell"== cell.data["source"] 

    assert 1 == len(cell.data["outputs"])
    assert "this is an output" == cell.data["outputs"][0]["data"]["text/plain"]

    assert 2 == cell.data["execution_count"]


def test_initiation_from_node_overwrite():
    node = new_code_cell("this is a cell", outputs=[new_output("execute_result", data={"text/plain": "this is an output"})])
    cell = JupyterCell(node, cell_type="raw")
    assert isinstance(cell.to_dict(), NotebookNode)
    assert "raw" == cell.data["cell_type"] 
    assert "this is a cell"== cell.data["source"] 
    assert "outputs" not in cell.data

def test_creation_from_object():
    def testfunc():
        return 'return value'

    cell = JupyterCell.from_object(testfunc)
    assert isinstance(cell.to_dict(), NotebookNode)
    assert cell.data.source == """
    def testfunc():
        return 'return value'
"""[1:]

def test_creation_from_code():
    code = """
    A = 5
    B = 2
    A + B
    """

    cell = JupyterCell.from_source_code(code)
    assert isinstance(cell.to_dict(), NotebookNode)
    assert cell.data.source == code

def test_creation_from_var_dict():
    import datetime
    d = {"integer": 5, "string": "value", "datelike":datetime.datetime(2020, 1, 1, 0, 0)}
    code = """
integer = 5
string = 'value'
datelike = datetime.datetime(2020, 1, 1, 0, 0)
"""[1:-1]

    cell = JupyterCell.from_variable_dict(d)
    assert isinstance(cell.to_dict(), NotebookNode)
    assert cell.data.source == code

def test_creation_from_var_kwds():
    import datetime
    d = {"integer": 5, "string": "value", "datelike":datetime.datetime(2020, 1, 1, 0, 0)}
    code = """
integer = 5
string = 'value'
datelike = datetime.datetime(2020, 1, 1, 0, 0)
"""[1:-1]

    cell = JupyterCell.from_variable_dict(**d)
    assert isinstance(cell.to_dict(), NotebookNode)
    assert cell.data.source == code