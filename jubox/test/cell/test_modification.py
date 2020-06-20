
"""
This test file contains tests for manipulating the
source of each cell class (test_classes), 
ie. the code in CodeCell, the markdown in MarkDownCell etc.
"""

import pytest
from utils import test_classes, get_test_id
from itertools import product

test_class_diff_combinations = [(a, b) for a, b in product(test_classes, test_classes) if a is not b]

@pytest.mark.parametrize("cls,", test_classes, ids=get_test_id)
def test_append(cls, *args):
    cell = cls("foo string")
    cell.append(" bar string")
    assert cell._node["source"] == "foo string bar string"

@pytest.mark.parametrize("cls,", test_classes, ids=get_test_id)
def test_append_another_cell(cls):
    cell = cls("foo string")
    cell.append(cls(" bar string"))
    assert cell._node["source"] == "foo string bar string"

@pytest.mark.parametrize("cls_a,cls_b", test_class_diff_combinations)
def test_append_wrong_type(cls_a, cls_b):
    cell = cls_a("foo string")
    with pytest.raises(TypeError):
        cell.append(cls_b(" bar string"))


@pytest.mark.parametrize("cls,", test_classes, ids=get_test_id)
def test_insert(cls):
    cell = cls("foo string")
    cell.insert(3, " bar")
    assert cell._node["source"] == "foo bar string"

@pytest.mark.parametrize("cls,", test_classes, ids=get_test_id)
def test_insert_another_cell(cls):
    cell = cls("foo string")
    cell.insert(3, cls(" bar"))
    assert cell._node["source"] == "foo bar string"

@pytest.mark.parametrize("cls_a,cls_b", test_class_diff_combinations)
def test_insert_wrong_type(cls_a, cls_b):
    cell = cls_a("foo string")
    with pytest.raises(TypeError):
        cell.insert(0, cls_b(" bar string"))


@pytest.mark.parametrize("cls,", test_classes, ids=get_test_id)
def test_overwrite(cls):
    cell = cls("foo string")
    cell.overwrite("now its bar string")
    assert cell._node["source"] == "now its bar string"

@pytest.mark.parametrize("cls,", test_classes, ids=get_test_id)
def test_overwrite_another_cell(cls):
    cell = cls("foo string")
    cell.overwrite(cls("now its bar string"))
    assert cell._node["source"] == "now its bar string"

@pytest.mark.parametrize("cls_a,cls_b", test_class_diff_combinations)
def test_overwrite_wrong_type(cls_a, cls_b):
    cell = cls_a("foo string")
    with pytest.raises(TypeError):
        cell.overwrite(cls_b(" bar string"))