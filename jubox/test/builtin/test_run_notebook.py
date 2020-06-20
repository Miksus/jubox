
from jubox import JupyterNotebook
from jubox.builtin import run_notebook

import datetime

def handle_success(**kwargs):
    print("Notebook succeeded")

def handle_failure(evalue, ename, traceback, extra, **kwargs):
    print("Notebook failed")
    extra["evalue"] = evalue
    extra["ename"] = ename
    extra["traceback"] = traceback

def handle_finally(**kwargs):
    print("Notebook finished")

def test_run_error(notebook_file_with_error, capsys):

    extra = {}

    run_notebook(
        notebook=notebook_file_with_error,
        on_failure=handle_failure,
        on_finally=handle_finally,
        silence=True,
        extra=extra
    )

    captured = capsys.readouterr()
    assert captured.out == "Notebook failed\nNotebook finished\n"
    assert extra["ename"] == "NameError"
    assert extra["evalue"] == "name 'un_specified_variable' is not defined"
    # Taking off the ipython version/serializaiton/whatever
    assert extra["traceback"].startswith("\x1b[1;31m---------------------------------------------------------------------------\x1b[0m\n\x1b[1;31mNameError\x1b[0m                                 Traceback (most recent call last)\n\x1b[1;32m<ipython-input-")
    assert extra["traceback"].endswith(">\x1b[0m in \x1b[0;36m<module>\x1b[1;34m\x1b[0m\n\x1b[1;32m----> 1\x1b[1;33m \x1b[0mun_specified_variable\x1b[0m\x1b[1;33m\x1b[0m\x1b[0m\n\x1b[0m\n\x1b[1;31mNameError\x1b[0m: name 'un_specified_variable' is not defined")
    
    
def test_run_success(notebook_file_task, capsys):

    run_notebook(
        notebook=notebook_file_task,
        on_success=handle_success,
        on_finally=handle_finally,
        silence=False,
    )

    captured = capsys.readouterr()
    assert captured.out == "Notebook succeeded\nNotebook finished\n"

def test_run_success_with_params(notebook_file_task, capsys):

    run_notebook(
        notebook=notebook_file_task,
        on_success=handle_success,
        on_finally=handle_finally,
        silence=False,
        parameters=dict(date=datetime.datetime.now(), number=10, category="b"),
        parameters_with_imports=True
    )

    captured = capsys.readouterr()
    assert captured.out == "Notebook succeeded\nNotebook finished\n"
