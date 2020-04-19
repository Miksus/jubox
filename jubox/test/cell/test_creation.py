
from jubox import JupyterCell
from nbformat.notebooknode import NotebookNode

def test_creation_empty():
    cell = JupyterCell()
    assert isinstance(cell.to_dict(), NotebookNode)

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