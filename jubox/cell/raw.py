
"""
Representation for Jupyter Notebook's raw blocks/cells
"""

from jubox.base import JupyterObject
from .base import JupyterCell

class RawCell(JupyterCell):
    cell_type = "raw"

    @classmethod
    def new_node(cls, *args, **kwargs):
        module = cls._get_nb_format()
        return module.new_raw_cell(*args, **kwargs)