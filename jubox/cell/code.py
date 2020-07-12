
"""
Representation for Jupyter Notebook's code blocks/cells
"""

import re
import copy
import types
import inspect
import logging
import warnings
from keyword import iskeyword

from jubox.base import JupyterObject
from .base import JupyterCell
from jubox import utils

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
        # TODO: Use ExecutePreprocessor.preprocess_cell instead
        nb = self.to_notebook()
        return nb(*args, **kwargs)

    def exec(self, globals=None, locals=None):
        """Execute the code in the cell with current Python interpreter

        Arguments:
        ----------
            globals {Dict} : Global variables for exec function. If undefined, the created global dict is returned
            locals {Dict} : Local variables for exec function
        """
        if globals is None:
            globals = {}
        exec(self.source, globals, locals)
        return globals

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
    def from_variable_dict(cls, var_dict=None, *, outputs=None, include_imports=False, **kwargs):
        """Create code cell from dictionary of variables. Useful for 
        creating parameter cells

        Arguments:
        ----------
            var_dict [Dict[str, Any]] : Dictionary of variables to parametrize
            outputs : Outputs to the cell, optional
            include_imports [bool] : Whether to determine and include the import statements to the cell
            **kwargs [Dict[str, Any]] : Updates var_dict
        
        Examples:
        ---------
            cell = CodeCell.from_variable_dict(
                a_string="2020-03-03",
                an_int=4,
                a_float=5.5,
                date=datetime.datetime(2020, 5, 10),
                ordered_dict=OrderedDict([("a", 2), ("b", 5)]),

                # Include the imports to the cell
                include_imports=True
            )
            cell.source
            >>>
                import datetime
                from collections import OrderedDict

                a_string = '2020-03-03'
                an_int = 4
                a_float = 5.5
                date = datetime.datetime(2020, 5, 10, 0, 0)
                ordered_dict = OrderedDict([('a', 2), ('b', 5)])
        """

        var_dict = {} if var_dict is None else var_dict
        var_dict.update(kwargs)

        regex_valid_init = r"([a-zA-Z0-9_]+[.])?[a-zA-Z0-9_]+\(.*\)" 
        # Regex allows: MyClass(x=5.5), datetime.datetime(year=2020, month=2, day=5), Counter()

        snippets = []
        imports = []
        for var, val in var_dict.items():
            repr_string = repr(val)
            module = type(val).__module__
            classname = type(val).__name__

            # Validation
            is_invalid_init = module != "builtins" and not bool(re.match(regex_valid_init, repr_string))
            is_invalid_varname = not var.isidentifier() or iskeyword(var)
            if is_invalid_init:
                raise ValueError(f"Variable's '{var}' repr does not produce valid initiation string: {repr_string}")
            elif is_invalid_varname:
                raise KeyError(f"Invalid variable name: {var}")

            # Variable declaration
            if isinstance(val, types.BuiltinFunctionType):
                repr_string = val.__name__ # Built in functions have odd repr, like sum: '<built-in function sum>'
            snippets.append(f"{var} = {repr_string}")

            # Import statement
            if include_imports and module != "builtins":

                has_module_in_repr = bool(re.match("[a-zA-Z0-9_]+[.].+", repr_string)) # For example datetime.datetime
                if has_module_in_repr:
                    # For example: repr(datetime.datetime.now()) --> "datetime.datetime(...)"
                    import_code = f"import {module}"
                else:
                    # For example: repr(datetime.datetime.now()) --> "datetime.datetime(...)"
                    import_code = f"from {module} import {classname}"
                imports.append(import_code)
        
        # Form the source code
        code = '\n'.join(snippets)
        if include_imports:
            code = '\n'.join(imports) + "\n\n" + code

        return cls.from_source_code(code, outputs=outputs)

# Fetch
    def get_output_as_html(self, **kwargs):
        warnings.warn("Method get_output_as_html is deprecated. Please use CodeCell.outputs.as_html", DeprecationWarning, stacklevel=2)
        return '<br>'.join([
            convert_to_html_format(output)
            for output in self["outputs"]
            if output_isin(output, **kwargs)
        ])

    def get_output_as_text(self, **kwargs):
        warnings.warn("Method get_output_as_html is deprecated. Please use CodeCell.outputs.as_plain", DeprecationWarning, stacklevel=2)
        return '\n'.join([
            convert_to_text_format(output)
            for output in self["outputs"]
            if output_isin(output, **kwargs)
        ])


    def get_outputs(self, mime_formats=None, output_types=None):
        warnings.warn("Method get_outputs is deprecated. Please use CodeCell.outputs.get", DeprecationWarning, stacklevel=2)
        return [
            output
            for output in self["outputs"]
            if output_isin(output, output_types=output_types, mime_formats=mime_formats)
        ]

# Additional properties
    @property
    def outputs(self):
        # TODO: Remove when accessors complete
        return self._node["outputs"]

    @property
    def execution_results(self):
        warnings.warn("Attribute execution_results is deprecated. Please use CodeCell.outputs.execute_results", DeprecationWarning, stacklevel=2)
        return [
            output for output in self.outputs
            if output["output_type"] == "execute_result"
        ]

    @property
    def display_data(self):
        warnings.warn("Attribute execution_results is deprecated. Please use CodeCell.outputs.display_data", DeprecationWarning, stacklevel=2)
        return [
            output for output in self.outputs
            if output["output_type"] == "display_data"
        ]

    @property
    def streams(self):
        warnings.warn("Attribute execution_results is deprecated. Please use CodeCell.outputs.streams", DeprecationWarning, stacklevel=2)
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
        return bool(self.outputs.errors)

    @property
    def has_execute_result(self):
        "Whether cell has execution results (returned variable)"
        return bool(self.outputs.execution_results)


def register_accessor(name):
    return utils.register_accessor(CodeCell, name)


# TODO: Remove the following functions
def convert_to_text_format(output):
    warnings.warn("Function convert_to_text_format is deprecated.", DeprecationWarning, stacklevel=2)
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
    warnings.warn("Function convert_to_html_format is deprecated.", DeprecationWarning, stacklevel=2)
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
    warnings.warn("Function output_isin is deprecated.", DeprecationWarning, stacklevel=2)
    isin_output_type = output_types is None or output["output_type"] in output_types 
    isin_mime_format = output_types is None or (
        output["output_type"] in ("display_data", "execute_result")
        and any(key in mime_formats for key in data)
    )
    logger.debug(f"Check: {output} --> Type: {isin_output_type}, Mime format: {isin_mime_format}")
    return isin_output_type and isin_mime_format
    