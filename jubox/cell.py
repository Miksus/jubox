
# WIP!
# EXPERIMENTIAL!

import copy

from nbformat.v4 import (
    new_notebook,

    new_code_cell, 
    new_markdown_cell, 
    new_raw_cell,

    new_output,
)
from nbconvert.filters import (
    wrap_text,
)

from nbconvert import exporters
from nbconvert import preprocessors

class JupyterCell:

    """Humane API for Jupyter Notebook Cells

    This class is a wrapper and extension 
    for nbformat.notebooknode.NotebookNode
    when NotebookNode points to cell data,
    ie. nbformat.v4.new_notebook().cells[0]
    """
    
    def __init__(self, cell=None):
        self.data = cell

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

    @classmethod
    def from_object(cls, obj):
        "Create cell from Python object (dumps the source to the cell)"
        source = inspect.getsource(obj)
        return cls.from_source_code(source)

    @classmethod
    def from_source_code(cls, string, outputs=None):
        "Create code cell from string"
        cell = new_code_cell(string)
        if outputs is not None:
            cell.outputs = outputs
        return cls(cell)

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
        cell["source"] = value
        if not inplace:
            return cell

# Representation
    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        width = 200
        if self["cell_type"] == "code":
            exe_count = self["execution_count"]

            source = self["source"]
            display = ''.join([
                output.get("data", {}).get("text/plain", "!NOT FOUND!")
                for output in self["outputs"] 
                if output["output_type"] == "display_data"
            ])
            execution = [
                output.get("data", {}).get("text/plain", "!NOT FOUND!")
                for output in self["outputs"] 
                if output["output_type"] == "execute_result"
            ]

            marginal = " " * (7 + len(str(exe_count)))

            # Blocks
            input_block = f"In [{exe_count}]: " + source.replace('\n', '\n' + marginal)
            display_block = marginal + display.replace("\n", "\n"+ marginal)
            execution_block = f"Out[{exe_count}]: " + execution.replace("\n", "\n" + marginal)

            string = input_block + "\n" + display_block + "\n" + execution_block

        else:
            string = self["source"]

        squeezed_string = wrap_text(string, width=width - 4)

        return squeezed_string

# Outputs
    @property
    def display_outputs(self):
        return [
            output.get("data", {}).get("text/plain", "!NOT FOUND!")
            for output in self["outputs"] 
            if output["output_type"] == "display_data"
        ]

# Fetch
    def get_outputs(self, output_type=None, format=None):
        return [
            output
            for output in self["outputs"]
            if output_is_type(output, output_type)
            and output_has_format(output, format)
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

# Problems with the following. setattr hits infinite recursion
#    def __getattr__(self, name):
#        "Fakes nbformat.notebooknode.NotebookNode behaviour"
#        return getattr(self.data, name)
#
#    def __setattr__(self, attr, val):
#        "Fakes nbformat.notebooknode.NotebookNode behaviour"
#        setattr(self.data, attr, val)

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


def output_has_format(output, format=None):
    if format is None:
        return True
    data = output.get("data")