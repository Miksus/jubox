
"""
Representation for Jupyter Notebook's code blocks/cells

See official documents for nbformat structure:
    https://readthedocs.org/projects/nbformat/downloads/pdf/latest/
"""

import re
import os
import copy
import logging
import warnings

import nbformat

from nbformat.v4 import new_notebook
from nbconvert import exporters
from nbconvert import preprocessors

from pathlib import Path

from jubox.cell import JupyterCell
from jubox.base import JupyterObject
from jubox import utils

logger = logging.getLogger(__name__)

class JupyterNotebook(JupyterObject):

    """Humane API for Jupyter Notebooks

    This class is a wrapper and extension 
    for nbformat.notebooknode.NotebookNode

    Class attributes:
    -----------
        nb_version [int] : The version of the node's notebook format, 
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
        elif isinstance(notebook, JupyterNotebook):
            self.node = notebook.node
            if hasattr(notebook, "file"):
                self.file = notebook.file
        elif notebook is None:
            # Creating empty notebook
            logger.debug("Initiating empty notebook")
            self.node = self._get_nb_format().new_notebook()
        elif isinstance(notebook, (list, tuple)):
            logger.debug("Initiating notebook from cells")
            self.node = self._get_nb_format().new_notebook()
            self.cells = notebook
        else:
            logger.debug("Initiating notebook from file")
            self.file = notebook

# Generic
    def __call__(self, *args, metadata=None, timeout=None, inplace=False, ignore=None, **kwargs):
        "Execute the code in the notebook"
        if ignore is not None:
            # Should not operate on copy thus running subset
            # of the notebook will have the outputs for the
            # full notebook 
            nb_main = copy.deepcopy(self) if not inplace else self
            nb_subset = nb_main.drop(inplace=False, **ignore)
            nb_subset(*args, metadata=metadata, timeout=timeout, inplace=True, ignore=None, **kwargs)
            return None if inplace else nb_main

        node = copy.deepcopy(self.node) if not inplace else self.node

        param_metadata = {} if metadata is None else metadata
        metadata = {"path": os.path.dirname(self.file) if hasattr(self, "file") else None}
        metadata.update(param_metadata)

        ep = preprocessors.ExecutePreprocessor(kernel_name=self.kernel_name, timeout=timeout)
        out = ep.preprocess(node, {'metadata': metadata})

        if not inplace:
            return JupyterNotebook.from_node(node)

    def __enter__(self):
        self.load()
        return self
    
    def __exit__(self, exception_type, exception_value, traceback):
        self.save()

# Items
    def __getitem__(self, i):
        "Index cells in the notebook"
        cells = self.cells[i]
        is_single_cell_index = not isinstance(cells, list)
        if is_single_cell_index:
            # Return one cell
            # Called like: self.cells[0]
            return cells
        else:
            return JupyterNotebook.from_cells(cells)


    def __setitem__(self, item, val):
        "Set cells in the notebook"
        if not isinstance(item, slice):
            # Overwrite the cell
            val = val._node if isinstance(val, JupyterCell) else val
            self.node.cells[item] = val
        else:
            values = [elem._node if isinstance(elem, JupyterCell) else elem for elem in val]
            self.node.cells[item] = values

    def __delitem__(self, item):
        "Delete a cell"
        del self.cells[item]

    def __reversed__(self):
        return reversed(self.cells)

    def __len__(self):
        return len(self.cells)

    def __iter__(self):
        "Iterate over cells"
        return iter(self.cells)

# IO
    def load(self):
        "(Re)load the notebook"
        # NOTE: nbformat.read does not like pathlib.Path
        self.node = nbformat.read(str(self.file), as_version=self.nb_version)

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
        nbformat.write(self.node, str(file), **kwargs)

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
        node = nbformat.reads(string, as_version=cls.nb_version)
        return cls(node)

    @classmethod
    def from_cells(cls, cells):
        "Construct notebook from list of cells (cells: nbformat.notebooknode.NotebookNode.cell)"
        obj = cls(None)
        obj.cells = [cells] if not isinstance(cells, list) else cells
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
        cell = cell._node if isinstance(cell, JupyterCell) else cell
        self.node.cells.append(cell)

    def insert(self, index, cell):
        "Insert cell to the notebook"
        cell = cell._node if isinstance(cell, JupyterCell) else cell
        self.node.cells.insert(index, cell)

# Validation
    def validate(self):
        "Validate the format of nbformat.notebooknode.NotebookNode"
        nbformat.validate(self.node)

# Cell fetch
    def get_cells(self, **kwargs):
        "Get cells matching given parameters (return nbformat.notebooknode.NotebookNode.cell)"
        warnings.warn("Method get_cells is deprecated. Please use JupyterNotebook.cells.get", DeprecationWarning, stacklevel=2)
        return [
            cell for cell in self.cells 
            if utils.cell_match(cell, **kwargs) 
        ]

    def get_indexes(self, **kwargs):
        "Get cell indexes of cells matching given parameters (return nbformat.notebooknode.NotebookNode.cell)"
        warnings.warn("Method get_indexes will be deprecated", DeprecationWarning, stacklevel=2)
        return [
            i for i, cell in enumerate(self.cells) 
            if utils.cell_match(**kwargs)
        ]

    def get(self, inplace=False, **kwargs):
        """Get sub JupyterNotebook from cells matching 
        given parameters and returns a new Notebook object"""
        cells = self.cells.get(**kwargs)
        if inplace:
            self.cells = cells
        else:
            return JupyterNotebook.from_cells(cells)

    def drop(self, inplace=False, **kwargs):
        cells = self.cells.drop(**kwargs)
        if inplace:
            self.cells = cells
        else:
            return JupyterNotebook.from_cells(cells)

# Additional properties
    @property
    def code_cells(self):
        warnings.warn("Attribute code_cells is deprecated. Please use JupyterNotebook.cells.code", DeprecationWarning, stacklevel=2)
        return [
            cell for cell in self
            if cell.cell_type == "code"
        ]

    @property
    def raw_cells(self):
        warnings.warn("Attribute raw_cells is deprecated. Please use JupyterNotebook.cells.raw", DeprecationWarning, stacklevel=2)
        return [
            cell for cell in self
            if cell.cell_type == "raw"
        ]

    @property
    def markdown_cells(self):
        warnings.warn("Attribute markdown_cells is deprecated. Please use JupyterNotebook.cells.markdown", DeprecationWarning, stacklevel=2)
        return [
            cell for cell in self
            if cell.cell_type == "markdown"
        ]

    @property
    def error_cells(self):
        warnings.warn("Attribute error_cells is deprecated. Please use JupyterNotebook.cells.errors", DeprecationWarning, stacklevel=2)
        return [
            cell for cell in self.code_cells
            if cell.cell_type == "code" 
            and cell.has_error
        ]
        
def register_accessor(name):
    return utils.register_accessor(JupyterNotebook, name)