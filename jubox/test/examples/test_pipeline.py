
import os
from pathlib import Path

import pytest

from jubox import JupyterNotebook, CodeCell, MarkdownCell
from nbformat.notebooknode import NotebookNode

def test_pipeline_generated():
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
    assert 13 == len(nb)
    assert 13 == len(nb)