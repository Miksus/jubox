
# https://readthedocs.org/projects/nbformat/downloads/pdf/latest/

import re
import os
import copy
import logging


import nbformat

from nbformat.v4 import new_notebook
from nbconvert import exporters
from nbconvert import preprocessors

from pathlib import Path

from .cell import JupyterCell
from .base import JupyterObject

logger = logging.getLogger(__name__)

class JupyterNotebook(JupyterObject):

    """Humane API for Jupyter Notebooks

    This class is a wrapper and extension 
    for nbformat.notebooknode.NotebookNode

    Class attributes:
    -----------
        as_version [int] : The version of the node's notebook format, 
            see https://nbformat.readthedocs.io/en/latest/
        kernel_name [str] : Kernel to use
            see https://nbformat.readthedocs.io/en/latest/
        html_exporter [HTMLExporter] : HTML exporter to use to
            form HTML version of the notebook. Override for
            custom formatting.
            see https://nbconvert.readthedocs.io/en/latest/api/exporters.html#nbconvert.exporters.HTMLExporter

    Attributes:
    -----------
        node [nbformat.notebooknode.NotebookNode] : Notebook data
        file [str, path-like] : File for the notebook (optional)
    
    Properties:
    -----------
        cells [List[JupyterCell]] : List of cells using Jubox's API. 
            To get the native representation of the cells, use 
            .node.cells or .cells.to_dict()
        metadata [nbformat.notebooknode.NotebookNode.metadata] : Metadata
            of the notebook. See https://nbformat.readthedocs.io/en/latest/

    """



    html_exporter = exporters.HTMLExporter()

    def __init__(self, notebook=None):
        if isinstance(notebook, nbformat.notebooknode.NotebookNode):
            logger.debug("Initiating notebook from nbformat.notebooknode.NotebookNode")
            self.node = notebook
        elif notebook is None:
            # Creating empty notebook
            logger.debug("Initiating empty notebook")
            self.node = new_notebook()
        elif isinstance(notebook, (list, tuple)):
            logger.debug("Initiating notebook from cells")
            self.node = new_notebook()
            self.cells = notebook
        else:
            logger.debug("Initiating notebook from file")
            self.file = notebook

# Generic
    def __call__(self, *args, metadata=None, timeout=None, inplace=False, **kwargs):
        "Execute the code in the notebook"
        node = copy.deepcopy(self.node) if not inplace else self.node

        param_metadata = {} if metadata is None else metadata
        metadata = {"path": os.path.dirname(self.file) if hasattr(self, "file") else None}
        metadata.update(param_metadata)

        ep = preprocessors.ExecutePreprocessor(kernel_name=self.kernel_name, timeout=timeout)
        out = ep.preprocess(node, {'metadata': metadata})

        if not inplace:
            return JupyterNotebook.from_node(node)

    def __iter__(self):
        "Iterate over cells"
        return iter(self.cells)

    def __enter__(self):
        self.load()
        return self
    
    def __exit__(self, exception_type, exception_value, traceback):
        self.save()

    def __getitem__(self, i):
        "Index cells in the notebook"
        cells = self.cells[i]
        if isinstance(i, slice):
            # Multiple cells --> a sub Jupyter Notebook
            return JupyterNotebook.from_cells(cells)
        else:
            return cells

    def __setitem__(self, item, val):
        "Set cells in the notebook"
        if not isinstance(item, slice):
            # Overwrite the cell
            val = val.to_dict() if isinstance(val, JupyterCell) else val
            self.node.cells[item] = val
        else:
            values = [elem.to_dict() if isinstance(elem, JupyterCell) else elem for elem in val]
            self.node.cells[item] = values

    def __delitem__(self, item):
        del self.node.cells[item]

# IO
    def load(self):
        "(Re)load the notebook"
        # NOTE: nbformat.read does not like pathlib.Path
        self.node = nbformat.read(str(self.file), as_version=self.as_version)

    def save(self):
        "Save the notebook to original path"
        self.to_ipynb(file=self.file)

#   Specific file types
    def to_html(self, file, **kwargs):
        "Put the notebook to a HTML file"
        self.to_file(file, exporter=self.html_exporter)

    def to_python(self, file, **kwargs):
        "Put the notebook to a Python file"
        exporter = exporters.PythonExporter(**kwargs)
        self.to_file(file, exporter=exporter)

    def to_slides(self, file, **kwargs):
        "Put the notebook to a slides file"
        exporter = exporters.SlidesExporter(**kwargs)
        self.to_file(file, exporter=exporter)

    def to_pdf(self, file, **kwargs):
        "Put the notebook to a PDF file"
        exporter = exporters.PDFExporter(**kwargs)
        self.to_file(file, exporter=exporter)
        
    def to_ipynb(self, file, **kwargs):
        "Put the notebook to a Jupyter Notebook file"
        nbformat.write(self.node, file, **kwargs)

#   Generic IO
    def to_file(self, file, *, exporter):
        "Put the notebook to a file using given exporter"
        (body, resources) = exporter.from_notebook_node(self.node)
        with open(file, mode="w") as f:
            f.write(body)

# representations
    def _repr_html_(self):
        "Render the notebook as HTML"
        exporter = self.html_exporter
        (body, resources) = exporter.from_notebook_node(self.node)
        return body

    def __str__(self):
        s_cells = [
            str(cell)
            for cell in self
        ]
        return '\n'.join(s_cells)

# Internal
    @property
    def node(self):
        """Get the nbformat.notebooknode.NotebookNode 
        representation of the notebook"""
        if not hasattr(self, "_node"):
            self.load()
        return self._node
    
    @node.setter
    def node(self, val):
        """Set nbformat.notebooknode.NotebookNode 
        representation of the notebook"""
        nbformat.validate(val)
        self._node = val


    @property
    def cells(self):
        """Get cells of the notebook"""
        return JupyterCell.from_list(self.node.cells)

    @cells.setter
    def cells(self, val):
        "Set cells in the nbformat.notebooknode.NotebookNode "
        val = [item.to_dict() if isinstance(item, JupyterCell) else item for item in val]
        self.node.cells = val

    @property
    def metadata(self):
        """Get the metadata of 
        nbformat.notebooknode.NotebookNode"""
        return self.node["metadata"]

    @metadata.setter
    def metadata(self, value):
        """Set the metadata of 
        nbformat.notebooknode.NotebookNode"""
        self.node["metadata"] = value

# Class methods
    @classmethod
    def from_string(cls, string):
        "Construct notebook from string"
        node = nbformat.reads(string, as_version=cls.as_version)
        return cls(node)

    @classmethod
    def from_cells(cls, cells):
        "Construct notebook from list of cells (cells: nbformat.notebooknode.NotebookNode.cell)"
        obj = cls(None)
        obj.cells = cells
        return obj

    @classmethod
    def from_node(cls, node):
        "Construct notebook from nbformat.notebooknode.NotebookNode"
        return cls(node)

# Functionalities
#   Clearing
    def clear_outputs(self, **kwargs):
        "Clear all outputs in the notebook"
        processor = preprocessors.ClearOutputPreprocessor(**kwargs)
        return self.process_node(processor, **kwargs)

    def clear_metadata(self, **kwargs):
        "Clear all metadata in the notebook"
        processor = preprocessors.ClearMetadataPreprocessor(**kwargs)
        return self.process_node(processor, **kwargs)

    def clear_tags(self, **kwargs):
        "Clear all tags in the notebook"
        processor = preprocessors.TagRemovePreprocessor(**kwargs)
        return self.process_node(processor, **kwargs)

    def process_node(self, preprocessor, inplace=False):
        """Process the nbformat.notebooknode.NotebookNode
        representation of the notebook with specified
        preprocessor"""
        node = copy.deepcopy(self.node) if not inplace else self.node
        preprocessor.preprocess(node, {})
        if not inplace:
            return JupyterNotebook.from_node(node)

    def append(self, cell):
        "Append cell to the notebook"
        cell = cell.data if isinstance(cell, JupyterCell) else cell
        self.node.cells.append(cell)

    def insert(self, index, cell):
        "Append cell to the notebook"
        cell = cell.data if isinstance(cell, JupyterCell) else cell
        self.node.cells.insert(index, cell)

# Validation
    def validate(self):
        "Validate the format of nbformat.notebooknode.NotebookNode"
        nbformat.validate(self.node)

#   Fetch
    def get_cells(self, cell_type=None, source=None, source_regex=None, tags=None, not_tags=None):
        "Get cells matching given parameters (return nbformat.notebooknode.NotebookNode.cell)"
        return [
            cell for cell in self.cells 
            if  cell_has_tags(cell, tags=tags, not_tags=not_tags) 
            and cell_is_type(cell, cell_type=cell_type)
            and cell_is_source(cell, source=source)
            and cell_match_source(cell, regex=source_regex)
        ]

    def get_cell_outputs(self, **kwargs):
        "Get cell outputs matching given parameters (return nbformat.notebooknode.NotebookNode.cell)"
        raise NotImplementedError
        cells = self.get_cells(cell_type="code", **kwargs)
        return [
            format_output(cell.outputs)
            for cell in cells
        ]

    def get(self, inplace=False, **kwargs):
        """Get sub JupyterNotebook from cells matching 
        given parameters and returns a new Notebook object"""
        cells = self.get_cells(**kwargs)
        if inplace:
            self.cells = cells
        else:
            return JupyterNotebook.from_cells(cells)

# TODO: Move the following logic under JupyterCell
def cell_has_tags(cell, tags=None, not_tags=None):

    cell_tags = cell["metadata"].get("tags", [])

    isin_allowed_tags = (
        any(tag in cell_tags for tag in tags) or tags is None
        if tags is not None else True
    )

    isin_disallowed_tags = (
        any(tag in cell_tags for tag in not_tags)
        if not_tags is not None else False
    )
    return isin_allowed_tags and not isin_disallowed_tags

def cell_is_type(cell, cell_type=None):
    if cell_type is None:
        return True

    cell_types = [cell_type] if isinstance(cell_type, str) else cell_type
    return cell["cell_type"] in cell_types

def cell_is_source(cell, source=None):
    if source is None:
        return True

    return cell["source"] == source

def cell_match_source(cell, regex=None):
    if regex is None:
        return True
        
    return re.match(regex, cell["source"])