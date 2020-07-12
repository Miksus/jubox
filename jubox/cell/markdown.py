
"""
Representation for Jupyter Notebook's markdown blocks/cells
"""


from jubox.base import JupyterObject
from .base import JupyterCell

class MarkdownCell(JupyterCell):
    cell_type = "markdown"

    @classmethod
    def new_node(cls, *args, **kwargs):
        module = cls._get_nb_format()
        return module.new_markdown_cell(*args, **kwargs)