
from jubox import CodeCell, RawCell, MarkdownCell
from nbformat.notebooknode import NotebookNode

from nbformat.v4 import new_code_cell, new_output, new_raw_cell

def test_initiation():
    outputs = [new_output("stream", name="stdout", text="an output")]
    cell = CodeCell("x = 5", execution_count=1, outputs=outputs)

    assert isinstance(cell._node, NotebookNode)
    assert cell._node.source == "x = 5"
    assert cell._node.cell_type == "code"
    assert len(cell._node.outputs) == 1
    assert cell._node.outputs is outputs
    assert cell._node.execution_count == 1


def test_creation_from_object():
    def testfunc():
        return 'return value'

    cell = CodeCell.from_object(testfunc)
    assert isinstance(cell._node, NotebookNode)
    assert cell._node.source == """
    def testfunc():
        return 'return value'
"""[1:]


def test_creation_from_var_dict():
    import datetime
    d = {"integer": 5, "string": "value", "datelike":datetime.datetime(2020, 1, 1, 0, 0)}
    code = """
integer = 5
string = 'value'
datelike = datetime.datetime(2020, 1, 1, 0, 0)
"""[1:-1]

    cell = CodeCell.from_variable_dict(d)
    assert isinstance(cell._node, NotebookNode)
    assert cell._node.source == code

def test_creation_from_var_kwds():
    import datetime
    d = {"integer": 5, "string": "value", "datelike":datetime.datetime(2020, 1, 1, 0, 0)}
    code = """
integer = 5
string = 'value'
datelike = datetime.datetime(2020, 1, 1, 0, 0)
"""[1:-1]

    cell = CodeCell.from_variable_dict(**d)
    assert isinstance(cell._node, NotebookNode)
    assert cell._node.source == code