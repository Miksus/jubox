# Structure of Jubox
> Jubox mainly extends `nbformat.notebooknode.NotebookNode`
using composition.

# Base and basics
## jubox.base.JupyterObject
> This is a base class for all of the Jubox classes. Contains
basic information about the nbformat version to use
and kernel name so that they can be overridden in one place.


# Notebook
## jubox.notebook.notebook.JupyterNotebook
> This class is a wrapper to `nbformat.notebooknode.NotebookNode`
where NotebookNode represents a notebook. When the notebook's
cell is accessed, instead of returning 
nbformat.notebooknode.NotebookNode, Jubox's representation of
the cell is created which are more feature complete and
flexible. When JupyterNotebook access a cell, it initiates 
a `JupyterCell` using factory method `JupyterCell.from_list_of_nodes`
that defines which subclass to use. 

> Most of the methods in JupyterNotebook are done not inplace
so a copy of the Notebook (and its node) is returned. Methods
that typically modify inplace in Python (like `.append` & `.insert`)
are done inplace though.


# Cells
## jubox.cell.cell.CellMeta
> This meta class for all of the cell classes. This basically
is a register for subclasses of `JupyterCell` so that
correct class can be created when a cell representation of
`nbformat.notebooknode.NotebookNode` is turned as Jubox's
representation.

## jubox.cell.cell.JupyterCell
> This class is a wrapper to `nbformat.notebooknode.NotebookNode`
where NotebookNode represents a cell. Its meta class is `CellMeta`. 
The actual node is stored in the attribute "_node" and any other instance
specific attributes should not be stored in this class or its
subclasses and they should be stored in the _node itself. 
Class attributes are okay.

> Most of the methods in JupyterCell are done inplace
so the cell (and its node) is modified without copying. Methods
that typically return a copy in Python (like `\_\_add\_\_`)
are done with copy though.

### jubox.cell.code_cell.CodeCell
> Subclass of `JupyterCell` where cell_type = code. `CodeCell` is
the code cells in notebooks. Has more functionalities than
other cell types as code cells are more complex.

### jubox.cell.code_cell.MarkdownCell
> Subclass of `JupyterCell` where cell_type = markdown. `MarkdownCell` is
the markdown cells in notebooks.

### jubox.cell.code_cell.RawCell
> Subclass of `JupyterCell` where cell_type = raw. `RawCell` is
the code cells in notebooks.