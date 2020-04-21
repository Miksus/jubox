
import pytest

from jubox import JupyterNotebook, JupyterCell


def test_get_tags():
    nb = JupyterNotebook([
        JupyterCell("first cell"),
        JupyterCell("second cell", tags=["tagged"]),
        JupyterCell("third cell", taggs=["Not this", "tagged"]),
    ])
    nb_of_tags = nb.get(tags=["tagged"], not_tags=["Not this"])
    assert isinstance(nb_of_tags, JupyterNotebook)
    assert 1 == len(nb_of_tags.node.cells)
    assert "second cell" == nb_of_tags.node.cells[0]["source"]

def test_get_cell_types():
    nb = JupyterNotebook([
        JupyterCell("first cell", cell_type="raw"),
        JupyterCell("second cell", cell_type="code"),
        JupyterCell("third cell", cell_type="markdown"),
    ])
    nb_of_tags = nb.get(cell_type=["code"])
    assert isinstance(nb_of_tags, JupyterNotebook)
    assert 1 == len(nb_of_tags.node.cells)
    assert "second cell" == nb_of_tags.node.cells[0]["source"]