
from nbformat.v4 import (
    new_markdown_cell, 
)

from jubox.base import JupyterObject
from .cell import JupyterCell

class MarkdownCell(JupyterCell):
    cell_type = "markdown"

    @staticmethod
    def new_node(*args, **kwargs):
        module = JupyterObject._get_nb_format()
        return module.new_markdown_cell(*args, **kwargs)