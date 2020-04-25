
# WIP!
# EXPERIMENTIAL!

import re
import copy
import inspect
import logging
from abc import ABC, abstractmethod, ABCMeta

from jubox.base import JupyterObject

import nbformat

from nbconvert.filters import (
    wrap_text, ansi2html, html2text,
    indent
)

from nbconvert import exporters
from nbconvert import preprocessors

logger = logging.getLogger(__name__)

# Registries
CELL_TYPES = {}
CUSTOM_CELLS = [] # Meant for user defined special classes that take higher priority

class CellMeta(type):
    """
    Metaclass to register provided cell classes
    so that correct class is chosen when Notebook
    initiates individual cells from nodes
    """

    def __new__(mcs, name, bases, class_dict):

        cls = type.__new__(mcs, name, bases, class_dict)
        try:
            CELL_TYPES[cls.cell_type] = cls
        except AttributeError:
            # Cell class has no cell_type thus 
            # it is considered as user defined
            # custom class taking higher priority
            CUSTOM_CELLS.append(cls)
        return cls

class JupyterCell(JupyterObject, metaclass=CellMeta):

    """Humane API for Jupyter Notebook Cells
    Don't use this class directly and rather 
    use its subclasses CodeCell, MarkdownCell
    and RawCell.

    This class is a wrapper, compositor or view
    for nbformat.notebooknode.NotebookNode
    when NotebookNode points to cell data,
    ie. nbformat.v4.new_notebook().cells[0]

    Only _node attribute is stored and all
    other should be put to the acutal data
    of the cell (_node).

    Properties:
    -----------
        node [nbformat.notebooknode.NotebookNode] : Copy of
            notebook data 
            NOTE: This is copy of the actual node. This is 
            read only property as otherwise the consistency
            between JupyterCell.node["cell_type"] and the 
            type of the Jubox cell (CodeCell, RawCell etc.) 
            cannot be maintained.

    Attributes:
    -----------
        _node [nbformat.notebooknode.NotebookNode] : Actual
            notebook node. Modifications are safe except
            modifying the attribute "cell_type".
    """

    new_node_func = None
    cell_type = None

    def __init__(self, cell=None, **kwargs):

        if cell is None:
            node = self.new_node()
        elif isinstance(cell, str):
            node = self.new_node(cell)
        elif isinstance(cell, nbformat.notebooknode.NotebookNode): #  
            node = cell
        elif isinstance(cell, JupyterCell):
            # Making copy and changing type
            node = copy.deepcopy(cell._node)
        else:
            raise TypeError(f"Invalid type: {type(cell)}")
        # We have private _node because otherwise 
        # cell_type cannot be enforced reasonably
        self._node = node
        self.set_node_attrs(**kwargs)
        self.validate()

    @abstractmethod
    def new_node(self, cell):
        "Create new nbformat.notebooknode.NotebookNode from the inputted cell"

    def validate(self):
        assert self.cell_type == self._node["cell_type"]

    def set_node_attrs(self, metadata=None, **kwargs):
        if kwargs:
            metadata = {} if metadata is None else metadata
            metadata.update(kwargs)

        if metadata is not None:
            self._node["metadata"] = metadata
        self._node["cell_type"] = self.cell_type

    def __delete__(self):
        "Delete cell"
        del self._node

    @property
    def node(self):
        "nbformat.notebooknode.NotebookNode representation of the cell"
        logger.warn("Returing copy of the node.")
        return copy.deepcopy(self._node)

# Factory
    @classmethod
    def from_list_of_nodes(cls, cells):
        # JupyterNotebook uses this method
        # for interfacing thus modifications
        # with care
        return [
            JupyterCell.from_node(cell)
            for cell in cells
        ]

    @classmethod
    def from_node(cls, node):
        # JupyterNotebook uses this method
        # for interfacing thus modifications
        # with care
        for cls_custom in CUSTOM_CELLS:
            try:
                cell = cls_custom(node)
            except TypeError:
                # Custom cell types should raise TypeError
                # if not applicable
                pass
            else:
                return cell
        else:
            # No (applicable) custom cells, using default
            cls_cell_type = CELL_TYPES[node["cell_type"]]
            return cls_cell_type(node)
    
    @classmethod
    def from_file(cls, file):
        "Create cell from a file"
        with open(file, "r") as f:
            code = f.read()
        return cls(code)

# Conversions
    def to_notebook(self):
        "nbformat.notebooknode.NotebookNode (Notebook level) representation of the cell"
        from jubox.notebook import notebook
        nb = notebook.JupyterNotebook([self])
        return nb

    def overwrite(self, value, inplace=True):
        cell = copy.deepcopy(self) if not inplace else self
        if isinstance(value, JupyterCell):
            value = value._node.source
        cell["source"] = value
        if not inplace:
            return cell

    def append(self, value:str):
        "Append string to the cell source"
        value = (
            value["source"] 
            if isinstance(value, (JupyterCell, nbformat.notebooknode.NotebookNode))
            else str(value)
        )
        src = self["source"]
        self["source"] = src + value

    def insert(self, index:int, value:str):
        "Insert string to the cell source"
        value = (
            value["source"] 
            if isinstance(value, (JupyterCell, nbformat.notebooknode.NotebookNode))
            else str(value)
        )
        src = self["source"]
        self["source"] = src[:index] + value + src[index:]

# Representation
    def __repr__(self):
        return f"{type(self).__name__}{repr(self._node)}"

    def __str__(self):
        width = 200
        intendation = 7
        if self["cell_type"] == "code":
            exe_count = self["execution_count"]
            intendation += len(str(exe_count)) - 1

            input_block = self["source"]
            display_block = ''.join([
                convert_to_text_format(output)
                for output in self["outputs"] 
                if output["output_type"] in ("display_data", "stream")
            ])
            execution_block = ''.join([
                convert_to_text_format(output)
                for output in self["outputs"] 
                if output["output_type"] == "execute_result"
            ])
            error_block = ''.join([
                convert_to_text_format(output)
                for output in self["outputs"] 
                if output["output_type"] == "error"
            ])

            input_block = indent(input_block, nspaces=intendation)
            display_block = indent(display_block, nspaces=intendation)
            execution_block = indent(execution_block, nspaces=intendation)
            error_block = indent(error_block, nspaces=intendation)

            input_block = f"In [{exe_count}]: " + input_block[intendation:]
            if execution_block != " " * intendation:
                execution_block = f"Out[{exe_count}]: " + execution_block[intendation:]
            if error_block != " " * intendation:
                error_block = f"Out[{exe_count}]: " + error_block[intendation:]

            string = ""
            for block in (input_block, display_block, execution_block, error_block):
                if block:
                    string += '\n' + block

        else:
            string = indent(self["source"], nspaces=intendation)

        squeezed_string = wrap_text(string, width=width)

        return squeezed_string

# Faking
    def __iter__(self):
        return iter(self._node)

    def __getitem__(self, val):
        "Fakes nbformat.notebooknode.NotebookNode behaviour"
        return self._node[val]

    def __setitem__(self, item, val):
        "Fakes nbformat.notebooknode.NotebookNode behaviour"
        self._node[item] = val

    @property
    def source(self):
        return self._node.source

    @source.setter
    def source(self, val):
        self._node.source = val

    @property
    def metadata(self):
        return self._node.source

    @metadata.setter
    def metadata(self, val):
        self._node.metadata = val


# Problems with the following. setattr & copy hits infinite recursion
#    def __getattr__(self, name):
#        "Fakes nbformat.notebooknode.NotebookNode behaviour"
#        return getattr(self._node, name)
#
    def __setattr__(self, attr, val):
        """Fakes nbformat.notebooknode.NotebookNode behaviour
        JupyterCell can only store data attribute. All other
        attributes should be class attributes or be put to 
        the data. This is only a convenient view to the cells"""
        if attr != "_node":
            setattr(self._node, attr, val)
        else:
            self.__dict__[attr] = val

# Boolean functions
# TODO: use these instead of functions in JupyterNotebook.get
    def has_tags(self, tags=None, not_tags=None):

        cell_tags = self["metadata"].get("tags", [])

        isin_allowed_tags = (
            any(tag in cell_tags for tag in tags) or tags is None
            if tags is not None else True
        )

        isin_disallowed_tags = (
            any(tag in cell_tags for tag in not_tags)
            if not_tags is not None else False
        )
        return isin_allowed_tags and not isin_disallowed_tags

    def is_type(self, cell_type=None):
        if cell_type is None:
            return True

        cell_types = [cell_type] if isinstance(cell_type, str) else cell_type
        return self["cell_type"] in cell_types

    def is_source(self, source=None):
        if source is None:
            return True

        return self["source"] == source

    def match_source(self, regex=None):
        if regex is None:
            return True
            
        return re.match(regex, self["source"])

    def is_type(self, *output_types):
        return self["output_type"] in output_types

