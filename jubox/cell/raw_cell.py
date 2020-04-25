
from nbformat.v4 import (
    new_raw_cell,
)

from jubox.base import JupyterObject
from .cell import JupyterCell

class RawCell(JupyterCell):
    cell_type = "raw"

    @staticmethod
    def new_node(*args, **kwargs):
        module = JupyterObject._get_nb_format()
        return module.new_raw_cell(*args, **kwargs)