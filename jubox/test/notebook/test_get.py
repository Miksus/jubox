
import pytest

from jubox import JupyterNotebook, RawCell, CodeCell, MarkdownCell


def test_get_tags():
    nb = JupyterNotebook([
        RawCell("first cell"),
        RawCell("second cell", tags=["tagged"]),
        RawCell("third cell", taggs=["Not this", "tagged"]),
    ])
    nb_of_tags = nb.get(tags=["tagged"], not_tags=["Not this"])
    assert isinstance(nb_of_tags, JupyterNotebook)
    assert 1 == len(nb_of_tags.node.cells)
    assert "second cell" == nb_of_tags.node.cells[0]["source"]

def test_get_cell_types():
    nb = JupyterNotebook([
        RawCell("first cell"),
        CodeCell("second cell"),
        MarkdownCell("third cell"),
    ])
    nb_of_tags = nb.get(cell_type=["code"])
    assert isinstance(nb_of_tags, JupyterNotebook)
    assert 1 == len(nb_of_tags.node.cells)
    assert "second cell" == nb_of_tags.node.cells[0]["source"]