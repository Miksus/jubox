
from jubox import CodeCell, MarkdownCell, RawCell

test_classes = [CodeCell, MarkdownCell, RawCell]

def get_test_id(tpl):
    return tpl.__name__