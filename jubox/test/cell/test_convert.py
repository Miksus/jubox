
import pytest

from jubox import CodeCell, MarkdownCell, RawCell, JupyterCell
from nbformat.notebooknode import NotebookNode

from nbformat.v4 import new_code_cell, new_markdown_cell, new_raw_cell

test_classes = [CodeCell, MarkdownCell, RawCell]

def get_test_id(tpl):
    return tpl.__name__

@pytest.mark.parametrize("cls,", test_classes, ids=get_test_id)
def test_merge(cls, *args):
    cell = cls("foo string")
    cell.append(" bar string")
    assert cell._node["source"] == "foo string bar string"

@pytest.mark.parametrize("cls,", test_classes, ids=get_test_id)
def test_append_another_cell(cls):
    cell = cls("foo string")
    cell.append(cls(" bar string"))
    assert cell._node["source"] == "foo string bar string"

@pytest.mark.parametrize("cls,", test_classes, ids=get_test_id)
def test_insert(cls):
    cell = cls("foo string")
    cell.insert(3, " bar")
    assert cell._node["source"] == "foo bar string"
