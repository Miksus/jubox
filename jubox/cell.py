
# WIP!
# EXPERIMENTIAL!

import re
import copy
import inspect
import logging

from .base import JupyterObject

import nbformat
from nbformat.v4 import (
    new_notebook,

    new_code_cell, 
    new_markdown_cell, 
    new_raw_cell,

    new_output,
)

from nbconvert.filters import (
    wrap_text, ansi2html, html2text,
    indent
)

from nbconvert import exporters
from nbconvert import preprocessors

logger = logging.getLogger(__name__)

class JupyterCell(JupyterObject):

    """Humane API for Jupyter Notebook Cells

    This class is a wrapper, compositor or view
    for nbformat.notebooknode.NotebookNode
    when NotebookNode points to cell data,
    ie. nbformat.v4.new_notebook().cells[0]

    Only data attribute is stored and all
    other should be put to the acutal data
    of the cell
    """
    

    default_cell_type = "code"

    # TODO: Use the following attribute
    # everywhere where new cell functions are used
    # to make the support for different versions of
    # nbformat less painful
    _new_cell_funcs = {
        "code" : new_code_cell,
        "markdown" : new_markdown_cell,
        "raw" : new_raw_cell,
    }
    
    def __init__(self, cell=None, *, cell_type=None, **kwargs):

        if isinstance(cell, str) or cell is None:
            cell_type = cell_type or self.default_cell_type
            args = () if cell is None else (cell,)
            cell = self._new_cell_funcs[cell_type](*args, **self._parse_kwargs(cell_type, **kwargs))
        elif isinstance(cell, nbformat.notebooknode.NotebookNode) or isinstance(cell, JupyterCell):
            cell_type = cell_type if cell_type is not None else cell["cell_type"]
            kwds = self._parse_kwargs(cell_type, **kwargs)
            cell["metadata"].update(kwds.get("metadata", {}))
            if cell_type == "code":
                cell["execution_count"] = kwds.get("execution_count", cell["execution_count"])
                cell["outputs"] = kwds.get("outputs", cell["outputs"])
            else:
                cell.pop("execution_count", None)
                cell.pop("outputs", None)
            cell["cell_type"] = cell_type 
        else:
            raise TypeError(f"Unknown cell conversion for type {type(cell)}")
        self.data = cell

    def __delete__(self):
        "Delete cell"
        del self.data

    def __call__(self, *args, timeout=None, metadata=None, inplace=False, **kwargs):
        "Run the cell"
        node = copy.deepcopy(self.node) if not inplace else self.node
        metadata = {} if metadata is None else metadata

        ep = preprocessors.ExecutePreprocessor(kernel_name=self.kernel_name, timeout=timeout)
        out = ep.preprocess(node, {'metadata': metadata})
        if not inplace:
            return node

    @property
    def node(self):
        "nbformat.notebooknode.NotebookNode (Notebook level) representation of the cell"
        nb_node = new_notebook()
        nb_node.cells = [self.data]
        return nb_node

    def to_dict(self):
        "Back to nbformat.notebooknode.NotebookNode representation of the cell"
        return self.data

# Factory
    @classmethod
    def from_list(cls, cells):
        return [
            cls(cell)
            for cell in cells
        ]

#   Code cells
    @classmethod
    def from_source_code(cls, string, **kwargs):
        "Create code cell from string of source code"
        cell = new_code_cell(string)
        return cls(cell, **kwargs)

    @classmethod
    def from_object(cls, obj):
        "Create cell from Python object (dumps the source to the cell)"
        source = inspect.getsource(obj)
        return cls.from_source_code(source)

    @classmethod
    def from_source_file(cls, file):
        "Create cell from a source file"
        with open(file, "r") as f:
            code = f.read()
        return cls.from_source_code(code)

    @classmethod
    def from_variable_dict(cls, var_dict=None, *, outputs=None, **kwargs):
        """Create code cell from dictionary of variables. Useful for 
        creating parameter cells"""
        var_dict = {} if var_dict is None else var_dict
        var_dict.update(kwargs)
        
        snippets = [
            f"{key} = {repr(val)}" 
            for key, val in var_dict.items()
        ]
        code = '\n'.join(snippets)
        return cls.from_source_code(code, outputs=outputs)

#   Other cells
    @classmethod
    def from_markdown(cls, string):
        "Create code cell from string"
        cell = new_markdown_cell(string)
        return cls(cell)

    @classmethod
    def from_raw(cls, string):
        "Create code cell from string"
        cell = new_raw_cell(string)
        return cls(cell)

# Conversions
    def astype(self, cell_type, inplace=False):
        cell = copy.deepcopy(self) if not inplace else self
        cell["cell_type"] = cell_type
        if not inplace:
            return cell

    def overwrite(self, value, inplace=False):
        cell = copy.deepcopy(self) if not inplace else self
        if isinstance(value, JupyterCell):
            value = value.data.source
        cell["source"] = value
        if not inplace:
            return cell

    def append(self, value:str):
        "Append string to the cell"
        value = (
            value["source"] 
            if isinstance(value, (JupyterCell, nbformat.notebooknode.NotebookNode))
            else str(value)
        )
        src = self["source"]
        self["source"] = src + value

    def insert(self, index:int, value:str):
        "Insert string to the cell"
        value = (
            value["source"] 
            if isinstance(value, (JupyterCell, nbformat.notebooknode.NotebookNode))
            else str(value)
        )
        src = self["source"]
        self["source"] = src[:index] + value + src[index:]

# Representation
    def __repr__(self):
        return repr(self.data)

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


# Fetch
    def get_output_as_html(self, **kwargs):
        return '<br>'.join([
            convert_to_html_format(output)
            for output in self["outputs"]
            if output_isin(output, **kwargs)
        ])

    def get_output_as_text(self, **kwargs):
        return '\n'.join([
            convert_to_text_format(output)
            for output in self["outputs"]
            if output_isin(output, **kwargs)
        ])


    def get_outputs(self, mime_formats=None, output_types=None):
        return [
            output
            for output in self["outputs"]
            if output_isin(output, output_types=output_types, mime_formats=mime_formats)
        ]

# Faking
    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, val):
        "Fakes nbformat.notebooknode.NotebookNode behaviour"
        return self.data[val]

    def __setitem__(self, item, val):
        "Fakes nbformat.notebooknode.NotebookNode behaviour"
        self.data[item] = val

    @property
    def source(self):
        return self.data.source

    @source.setter
    def source(self, val):
        self.data.source = val

    @property
    def cell_type(self):
        return self.data.cell_type

    @cell_type.setter
    def cell_type(self, val):
        self.data.cell_type = val

    @property
    def metadata(self):
        return self.data.source

    @metadata.setter
    def metadata(self, val):
        self.data.metadata = val


# Problems with the following. setattr & copy hits infinite recursion
#    def __getattr__(self, name):
#        "Fakes nbformat.notebooknode.NotebookNode behaviour"
#        return getattr(self.data, name)
#
#    def __setattr__(self, attr, val):
#        """Fakes nbformat.notebooknode.NotebookNode behaviour
#        JupyterCell can only store data attribute. All other
#        attributes should be class attributes or be put to 
#        the data. This is only a convenient view to the cells"""
#        if attr != "data":
#            setattr(self.data, attr, val)

# Boolean functions
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



# Additional properties
    @property
    def has_output(self):
        return bool(self.data.get("outputs", False))

#   Code cells
    @property
    def has_error(self):
        "Whether cell has error in output"
        outputs = self.data.get("outputs", [])
        return any(
            output["output_type"] == "error"
            for output in outputs
        )

    @property
    def has_execute_result(self):
        "Whether cell has execution result (returned variable)"
        return any(
            output["output_type"] == "execute_result"
            for output in outputs
        )

# Util methods
    @staticmethod
    def _parse_kwargs(cell_type, outputs=None, execution_count=None, metadata=None, **kwargs):
        
        metadata = {} if metadata is None else metadata
        metadata.update(kwargs)
        if cell_type == "code":
            kwds = {}
            if outputs is not None:
                kwds["outputs"] = outputs
            if execution_count is not None:
                kwds["execution_count"] = execution_count
            kwds["metadata"] = metadata
            return kwds
        else:
            if outputs is not None:
                metadata.update({"outputs": outputs})
            if execution_count is not None:
                metadata.update({"execution_count": execution_count})
            return {"metadata": metadata}

# MIME types: https://www.freeformatter.com/mime-types-list.html

def convert_to_text_format(output):
    if output["output_type"] == "stream":
        return output["text"]

    elif output["output_type"] in ("display_data", "execute_result"):
        data = output["data"]
        if "text/plain" in data:
            text = data["text/plain"]
        elif "text/html" in data:
            text = html2text(data["text/html"])
        else:
            text = ""

    elif output["output_type"] == "error":
        text = '\n'.join(output["traceback"])

    else:
        raise KeyError(f"Invalid output type of output: {output['output_type']}")

    logger.debug(f"Conversion: {output} --> {text}")
    return text

def convert_to_html_format(output):
    
    if output["output_type"] == "stream":
        html = '<br>'.join(ansi2html(output["text"]))
        

    elif output["output_type"] in ("display_data", "execute_result"):
        data = output["data"]
        if "text/html" in data:
            logger.debug("Display output as  output to HTML")
            html = data["text/html"]
        elif "text/plain" in data:
            html = ansi2html(data["text/plain"])
        else:
            html = ""

    elif output["output_type"] == "error":
        html = '<br>'.join(ansi2html(lvl) for lvl in output["traceback"])
    else:
        raise KeyError(f"Invalid output type of output: {output['output_type']}")
    
    logger.debug(f"Conversion: {output} --> {html}")
    return html


def output_isin(output, output_types=None, mime_formats=None):

    isin_output_type = output_types is None or output["output_type"] in output_types 
    isin_mime_format = output_types is None or (
        output["output_type"] in ("display_data", "execute_result")
        and any(key in mime_formats for key in data)
    )
    logger.debug(f"Check: {output} --> Type: {isin_output_type}, Mime format: {isin_mime_format}")
    return isin_output_type and isin_mime_format
    