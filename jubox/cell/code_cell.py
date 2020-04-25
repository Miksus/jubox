
import re
import copy
import inspect
import logging

from jubox.base import JupyterObject
from .cell import JupyterCell

import nbformat

from nbconvert.filters import (
    wrap_text, ansi2html, html2text,
    indent
)

from nbconvert import exporters
from nbconvert import preprocessors

logger = logging.getLogger(__name__)

class CodeCell(JupyterCell):

    """
    Code cell in JupyterNotebook
    """

    cell_type = "code"

    @classmethod
    def new_node(cls, *args, **kwargs):
        module = cls._get_nb_format()
        return module.new_code_cell(*args, **kwargs)

    def set_node_attrs(self, outputs=None, execution_count=None, **kwargs):
        if outputs is not None:
            self._node["outputs"] = outputs
        if execution_count is not None:
            self._node["execution_count"] = execution_count
        super().set_node_attrs(**kwargs)

    def __call__(self, *args, **kwargs):
        "Run the cell"
        nb = self.to_notebook()
        return nb(*args, **kwargs)


    @classmethod
    def from_source_code(cls, string, **kwargs):
        "Create code cell from string of source code"
        cell = cls._get_nb_format().new_code_cell(string)
        return cls(cell, **kwargs)

    @classmethod
    def from_object(cls, obj):
        "Create cell from Python object (dumps the source to the cell)"
        source = inspect.getsource(obj)
        return cls.from_source_code(source)

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

# Additional properties
    @property
    def outputs(self):
        return self._node["outputs"]

    @property
    def execution_results(self):
        return [
            output for output in self.outputs
            if output["output_type"] == "execute_result"
        ]

    @property
    def display_data(self):
        return [
            output for output in self.outputs
            if output["output_type"] == "display_data"
        ]

    @property
    def streams(self):
        return [
            output for output in self.outputs
            if output["output_type"] == "stream"
        ]

    @property
    def has_output(self):
        return bool(self._node.get("outputs", False))

    @property
    def has_error(self):
        "Whether cell has error in output"
        outputs = self._node.get("outputs", [])
        return any(
            output["output_type"] == "error"
            for output in outputs
        )

    @property
    def has_execute_result(self):
        "Whether cell has execution results (returned variable)"
        return len(self.execution_results) > 0


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
    