
import copy

from .notebook import JupyterNotebook
from ..cell import JupyterCell
from jubox import utils 

class Accessor:

    def __init__(self, cls):
        self.cls = cls


    def __get__(self, instance, owner):
        # instance.self
        # where self is CLASS attribute of owner
        # and instance is instance of owner class

        return self.cls(instance)

    def __set__(self, instance, value):
        # instance.self = value
        # where self is CLASS attribute
        return self.cls(instance).__set__(instance, value)

    def __delete__(self, instance):
        # del instance.self
        # where self is CLASS attribute
        return self.cls(instance).__delete__(instance)


def register_accessor(name):
    # Inspiration: https://github.com/pandas-dev/pandas/blob/c21be0562a33d149b62735fc82aff80e4d5942f5/pandas/core/accessor.py#L197
    def wrapper(cls):
        setattr(JupyterNotebook, name, Accessor(cls))
        return cls
    return wrapper


@register_accessor("cells")
class Cells:
    """
    
    Examples:
    ---------
        nb.cells
    """
    def __init__(self, notebook):
        self._nb = notebook

    @property
    def code(self):
        return [
            cell
            for cell in self
            if cell.cell_type == "code" 
        ]

    @property
    def markdown(self):
        return [
            cell
            for cell in self
            if cell.cell_type == "markdown" 
        ]

    @property
    def raw(self):
        return [
            cell
            for cell in self
            if cell.cell_type == "raw" 
        ]

    @property
    def outputs(self):
        return [
            cell.output
            for cell in self
            if cell.cell_type == "code" 
        ]

    @property
    def errors(self):
        return [
            cell
            for cell in self
            if cell.cell_type == "code" 
            and cell.has_error
        ]

    def __getitem__(self, item):
        """Index cells in the notebook. 
        return List[JupyterCell]"""

        if isinstance(item, (slice, int)):
            return list(self)[item]
        elif is_bool_array(item):
            return [
                cell
                for i, cell in enumerate(self)
                if item[i]
            ]
        elif is_index_array(item):
            cells = list(self)
            return [
                cells[i]    
                for i in item
            ]
        else:
            raise IndexError(f"Invalid index: {item}")
        

    def __setitem__(self, item, val):
        "Set cells in the notebook"
        node = self._nb.node

        if isinstance(item, int):
            node.cells[item] = utils.to_cell_node(val)

        elif isinstance(item, slice):
            # Overwrite the cell
            node.cells[item] = [utils.to_cell_node(item) for item in val]

        elif is_bool_array(item):
            values = [utils.to_cell_node(val) for cell in val]
            for i, (cell, change) in enumerate(zip(node.cells, item)):
                if change:
                    node.cells[i] = values[i]

        elif is_index_array(item):
            values = [utils.to_cell_node(val) for cell in val]
            if len(node.cells) != len(values):
                raise IndexError

            for i in item:
                node.cells[i] = values[i]

    def __delitem__(self, item):
        "Delete a cell"
        node = self._nb.node
        del node.cells[item]

    def __reversed__(self):
        orig_node = self._nb.node
        node = copy.copy(orig_node)
        node.cells = list(reversed(node.cells))
        return self._nb.from_node(node)

    def __iter__(self):
        for cell in self._nb.node.cells:
            yield JupyterCell.from_node(cell)

    def __len__(self):
        return len(self._nb.node.cells)

    def __set__(self, instance, value):
        values = [
            utils.to_cell_node(item)
            for item in value
        ]
        self._nb.node.cells = values

    def __delete__(self, instance):
        self._nb.node.cells = []

    def get(self, **kwargs):
        return [
            cell for cell in self._nb.cells 
            if utils.cell_match(cell, **kwargs)
        ]

    def drop(self, **kwargs):
        return [
            cell for cell in self._nb.cells 
            if not utils.cell_match(cell, **kwargs)
        ]


def is_bool_array(item):
    # Possibly use
    try:
        from pandas.core.common import is_bool_indexer
        return is_bool_indexer(item)
    except ImportError:
        if all(isinstance(val, bool) for val in item):
            return True
        else:
            return False

def is_index_array(item):
    if all(isinstance(val, int) for val in item):
        return True
    else:
        return False