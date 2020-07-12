
import pytest

from jubox import CodeCell
from nbformat.notebooknode import NotebookNode

from nbconvert.preprocessors import CellExecutionError

def test_exection():
    cell = CodeCell("'foo' + 'bar'")
    cell(inplace=True)
    assert 1 == len(cell.outputs)
    assert 'foobar' in str(cell.outputs[0])

def test_exection_with_error():
    cell = CodeCell("foo")
    with pytest.raises(CellExecutionError):
        cell(inplace=True)
    assert 1 == len(cell.outputs)
    assert 'NameError' in str(cell.outputs[0])

def test_exec():
    cell = CodeCell("exec_var = 'foo' + 'bar'")
    cell_vars = cell.exec()
    assert 0 == len(cell.outputs)
    assert 'foobar' == cell_vars["exec_var"]