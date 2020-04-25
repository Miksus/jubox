
import pytest

from jubox import CodeCell, MarkdownCell, RawCell, JupyterNotebook
from nbformat.notebooknode import NotebookNode

from nbformat.v4 import new_code_cell, new_markdown_cell, new_raw_cell

from utils import test_classes, get_test_id

@pytest.mark.parametrize("cls,", test_classes, ids=get_test_id)
def test_cell_to_notebook(cls):
    cell = MarkdownCell("a cell")
    nb = cell.to_notebook()
    assert isinstance(nb, JupyterNotebook)
    assert nb.cells[0]._node is cell._node