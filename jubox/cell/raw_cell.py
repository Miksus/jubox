
from nbformat.v4 import (
    new_raw_cell,
)

from jubox.base import JupyterObject
from .cell import JupyterCell

class RawCell(JupyterCell):
    cell_type = "raw"

    @classmethod
    def new_node(cls, *args, **kwargs):
        module = cls._get_nb_format()
        return module.new_raw_cell(*args, **kwargs)