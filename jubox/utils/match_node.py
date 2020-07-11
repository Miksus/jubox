
import re

def cell_match(cell, 
               tags=None, not_tags=None,
               cell_type=None,
               source=None,
               source_match=None,
               output_type=None,
               empty=None):
    "Whether a cell matches given characteristics"
    return all((
        cell_has_tags(cell, tags=tags, not_tags=not_tags),
        cell_is_type(cell, cell_type=cell_type),
        cell_is_source(cell, source=source),
        cell_match_source(cell, regex=source_match),
        cell_has_output(cell, output_type=output_type),
        True if empty is None else cell_is_empty(cell) if empty else not cell_is_empty(cell),
    ))

def cell_has_tags(cell, tags=None, not_tags=None):
    "Whether the cell has specified tags and no disallowed tags"
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
    "Whether the cell type is specified"
    if cell_type is None:
        return True

    cell_types = [cell_type] if isinstance(cell_type, str) else cell_type
    return cell["cell_type"] in cell_types

def cell_is_source(cell, source=None):
    "Whether the cell source is exactly"
    if source is None:
        return True

    return cell["source"] == source

def cell_match_source(cell, regex=None):
    "Whether the cell source matches regex"
    if regex is None:
        return True
        
    return re.match(regex, cell["source"])

def cell_has_output(cell, output_type=None):
    "Whether the cell has given cell type"
    if output_type is None:
        return True
    output_types = [output_type] if isinstance(output_type, str) else output_type

    cell_outputs = cell.get("outputs", [])
    if not cell_outputs:
        return False
    return any(
        output["output_type"] in output_types for output in cell_outputs
    )

def cell_is_empty(cell):
    "Whether the source of the cell is empty"
    return bool(cell["source"])