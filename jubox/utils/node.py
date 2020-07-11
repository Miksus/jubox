
import nbformat

def to_cell_node(item):
    if hasattr(item, "_node"):
        return item._node
    
    elif is_node(item) and not is_notebook_node(item):
        return item

    else:
        raise TypeError(f"Cannot turn to cell node: {type(item)}")

def is_notebook_node(item):
    try:
        nbformat.validate(item)
    except:
        return False
    else:
        return True

def is_node(item):
    return isinstance(item, nbformat.NotebookNode)
