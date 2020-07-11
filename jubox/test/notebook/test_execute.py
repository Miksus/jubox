
import os
from pathlib import Path

from nbconvert.preprocessors import CellExecutionError

import pytest

from jubox import JupyterNotebook, JupyterCell


def test_execute_inplace(notebook_file_unrun):
    nb = JupyterNotebook(notebook_file_unrun)

    with pytest.raises(IndexError):
        # Should not have outputs thus error is raised
        nb.node.cells[-1].outputs[0]

    nb(inplace=True)

    assert nb.node.cells[-1].outputs[0]["data"]["text/plain"] == "'foobar'"

def test_execute_inplace_error(notebook_file_with_error):
    nb = JupyterNotebook(notebook_file_with_error)

    with pytest.raises(IndexError):
        # Should not have outputs thus error is raised
        nb.node.cells[-1].outputs[0]

    with pytest.raises(CellExecutionError):
        nb(inplace=True)

    with pytest.raises(IndexError):
        # Should not have outputs at last cell thus error is raised
        nb.node.cells[-1].outputs[-1]

    assert "NameError" == nb.node.cells[1].outputs[0]["ename"]
    assert "name 'un_specified_variable' is not defined" == nb.node.cells[1].outputs[0]["evalue"]

def test_execute_not_inplace_error(notebook_file_with_error):
    nb = JupyterNotebook(notebook_file_with_error)

    with pytest.raises(IndexError):
        # Should not have outputs thus error is raised
        nb.node.cells[-1].outputs[0]

    with pytest.raises(CellExecutionError):
        nb_2 = nb(inplace=False)

    with pytest.raises(NameError):
        nb_2 # This variable should not exist

    with pytest.raises(IndexError):
        # Should not have outputs at last cell thus error is raised
        nb.node.cells[-1].outputs[-1]

    for cell in nb.node.cells:
        # No outputs should be stored. Inplace should be used otherwise
        assert [] == cell["outputs"]

def test_execute_not_inplace(notebook_file_unrun):
    nb = JupyterNotebook(notebook_file_unrun)

    with pytest.raises(IndexError):
        # Should not have outputs thus error is raised
        nb.node.cells[-1].outputs[0]

    nb_run = nb(inplace=False)

    assert nb_run.node.cells[-1].outputs[0]["data"]["text/plain"] == "'foobar'"

def test_execute_ignore_inplace(notebook_file_task):
    nb = JupyterNotebook(notebook_file_task)
    nb.clear_outputs()
    nb(inplace=True, ignore=dict(tags=["result"]))

    assert len(nb.cells[1].outputs) == 1
    assert len(nb.cells[-1].outputs) == 0
    assert len(nb.cells.get(tags=["result"])[-1].outputs) == 0

    with pytest.raises(CellExecutionError):
        # Should raise exception as some of the variables
        # are undefined
        nb(inplace=True, ignore=dict(tags=["parameters"]))

def test_execute_ignore_not_inplace(notebook_file_task):
    nb = JupyterNotebook(notebook_file_task)
    nb.clear_outputs()
    nb_result = nb(inplace=False, ignore=dict(tags=["result"]))

    assert len(nb_result.cells[1].outputs) == 1
    assert len(nb_result.cells[-1].outputs) == 0
    assert len(nb_result.cells.get(tags=["result"])[-1].outputs) == 0

    with pytest.raises(CellExecutionError):
        # Should raise exception as some of the variables
        # are undefined
        nb(inplace=False, ignore=dict(tags=["parameters"]))