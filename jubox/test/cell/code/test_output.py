
from textwrap import dedent

import re

import pytest
from jubox import CodeCell
from nbconvert.preprocessors import CellExecutionError

def test_plain_text():
    
    cell = CodeCell(dedent("""
        from IPython.core.display import display, HTML, Image
        display(HTML('<h1>Hello, world!</h1>'))
        import warnings

        print("Hello")
        warnings.warn("Bye")
        print("world")
        warnings.warn("world")
        not_defined
    """))
    with pytest.raises(CellExecutionError):
        cell(inplace=True)

    expected_start = (
        #'<IPython.core.display.HTML object>\n'
        'Hello\n'
        'world\n'
        '\n'
    )

    expected_end = (
        '---------------------------------------------------------------------------\n'
        'NameError                                 Traceback (most recent call last)\n<ipython-input-1-c055c966680c> in <module>\n'
        '      7 print("world")\n'
        '      8 warnings.warn("world")\n'
        '----> 9 not_defined\n'
        '\n'
        'NameError: name \'not_defined\' is not defined\n',
        '<IPython.core.display.HTML object>'
    )

    actual = cell.outputs.as_plain()

    assert actual.startswith(expected_start)
    assert 'UserWarning: Bye' in actual
    assert 'UserWarning: world\n' in actual
    assert actual.endswith(expected_end)



def test_html():
    
    cell = CodeCell(dedent("""
        from IPython.core.display import display, HTML, Image
        display(HTML('<h1>Hello, world!</h1>'))
        import warnings

        print("Hello")
        warnings.warn("Bye")
        print("world")
        warnings.warn("world")
        not_defined
    """))
    with pytest.raises(CellExecutionError):
        cell(inplace=True)

    expected_start = (
        #'<IPython.core.display.HTML object>\n'
        'Hello<br>world<br>\n'
    )

    expected_end = (
        '---------------------------------------------------------------------------<br>'
        'NameError                                 Traceback (most recent call last)<br>'
        '<ipython-input-1-c055c966680c> in <module><br>      7 print("world")<br>'
        '      8 warnings.warn("world")<br>----> 9 not_defined<br><br>'
        'NameError: name \'not_defined\' is not defined\n'
        '<h1>Hello, world!</h1>'
    )

    actual = cell.outputs.as_html(use_css=False)

    assert actual.startswith(expected_start)
    assert 'ipykernel_launcher.py:6: UserWarning: Bye<br>' in actual
    assert 'ipykernel_launcher.py:8: UserWarning: world<br>' in actual
    assert actual.endswith(expected_end)