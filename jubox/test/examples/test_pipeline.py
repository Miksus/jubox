
import os
from pathlib import Path

import pytest

from jubox import JupyterNotebook, CodeCell, MarkdownCell
from nbformat.notebooknode import NotebookNode

from nbconvert.preprocessors import CellExecutionError

def test_pipeline_generated():

    try:
        import pandas as pd
    except ModuleNotFoundError:
        pytest.skip("Missing extra test dependency.")

    import datetime
    def transform_func(df):
        # start_date and category are globals given in the notebook
        mask_time = df['date'] > start_time
        mask_category = df['category'] == category
        return df[mask_time & mask_category]

    nb = JupyterNotebook([
        MarkdownCell("# This is a pipeline example"),
        MarkdownCell("## Imports"),
        CodeCell("import datetime \nimport pandas as pd"),
        MarkdownCell("## Params"),
        CodeCell.from_variable_dict(start_time=datetime.datetime(2020, 3, 1), category="Blue"),
        
        MarkdownCell("# Functions"),
        CodeCell.from_object(transform_func),
        
        MarkdownCell("# Extract"),
        CodeCell("""df = pd.DataFrame(
            {
                'date': pd.date_range('2020-02-01', periods=50, freq='D'), 
                'category': np.random.choice(['Blue', 'Red'], size=50)
            }
        )"""),
        MarkdownCell("# Transform"),
        CodeCell("""df = transform_func(df)"""),
        MarkdownCell("# Display"),
        CodeCell("""df"""),
        CodeCell("""not_specified_variable"""),
    ])
    assert 14 == len(nb)

    with pytest.raises(CellExecutionError):
        nb(inplace=True)

    err_cell = nb.cells.errors[0]
    html_tb = err_cell.outputs.as_html()

    assert "NameError" in html_tb
    assert "is not defined" in html_tb
    assert "Traceback (most recent call last)" in html_tb
    
    text_tb = err_cell.outputs.as_html()
    assert "NameError" in text_tb
    assert "is not defined" in text_tb
    assert "Traceback (most recent call last)" in text_tb