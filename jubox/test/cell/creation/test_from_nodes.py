
import pytest

from jubox import CodeCell, MarkdownCell, RawCell, JupyterCell
from nbformat.notebooknode import NotebookNode

from nbformat.v4 import new_code_cell, new_markdown_cell, new_raw_cell

test_classes = [(CodeCell,), (MarkdownCell,), (RawCell,)]

def get_test_id(tpl):
    return tpl[0].__name__

@pytest.mark.parametrize("cls", test_classes, ids=get_test_id)
def test_initiation_from_raw_node(cls):
    cls = cls[0]

    original_node = new_raw_cell("This is test")
    cell = cls(original_node)

    assert cell._node is original_node # Should be same object
    assert cell._node["source"] == "This is test"
    assert cell._node.cell_type == cls.cell_type

@pytest.mark.parametrize("cls", test_classes, ids=get_test_id)
def test_initiation_from_code_node(cls):
    cls = cls[0]

    original_node = new_code_cell("This is test")
    cell = cls(original_node)

    assert cell._node is original_node # Should be same object
    assert cell._node["source"] == "This is test"
    assert cell._node.cell_type == cls.cell_type

@pytest.mark.parametrize("cls", test_classes, ids=get_test_id)
def test_initiation_from_markdown_node(cls):
    cls = cls[0]

    original_node = new_markdown_cell("This is test")
    cell = cls(original_node)

    assert cell._node is original_node # Should be same object
    assert cell._node["source"] == "This is test"
    assert cell._node.cell_type == cls.cell_type