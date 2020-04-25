
import pytest

from jubox import CodeCell, MarkdownCell, RawCell, JupyterCell
from nbformat.notebooknode import NotebookNode

from nbformat.v4 import new_code_cell, new_markdown_cell, new_raw_cell

test_classes = [(CodeCell,), (MarkdownCell,), (RawCell,)]

def get_test_id(tpl):
    return tpl[0].__name__

@pytest.mark.parametrize("cls", test_classes, ids=get_test_id)
def test_initiation_from_empty(cls):
    cls = cls[0]
    cell = cls()

    assert isinstance(cell._node, NotebookNode)
    assert cell._node.source == ""
    assert cell._node.cell_type == cls.cell_type

@pytest.mark.parametrize("cls", test_classes, ids=get_test_id)
def test_initiation_from_string(cls):
    cls = cls[0]
    cell = cls("This is a test cell")

    assert isinstance(cell._node, NotebookNode)
    assert cell._node.source == "This is a test cell"
    assert cell._node.cell_type == cls.cell_type

@pytest.mark.parametrize("cls", test_classes, ids=get_test_id)
def test_initiation_from_string_with_tags(cls):
    cls = cls[0]
    cell = cls("This is a test cell", tags=["tagged"])

    assert isinstance(cell._node, NotebookNode)
    assert cell._node.source == "This is a test cell"
    assert cell._node.cell_type == cls.cell_type
    assert cell._node.metadata.tags == ["tagged"]
