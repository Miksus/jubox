
import pytest
import os
from pathlib import Path

# Testing utils
# https://stackoverflow.com/a/33515264
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))


# Fixtures
@pytest.fixture
def notebook_folder():
    return str(Path(os.path.dirname(__file__)) / "test_files")

@pytest.fixture#(scope="module")
def notebook_path(tmpdir):
    # Returns pathlib.Path

    path = Path(os.path.dirname(__file__)) / "test_files" / "nb_simple.ipynb"

    fh = tmpdir.join("notebook.ipynb")
    with open(path) as f:
        fh.write(f.read())
    filename = os.path.join( fh.dirname, fh.basename )
    return Path(filename)

@pytest.fixture#(scope="module")
def notebook_file(tmpdir):
    "Typical production like Jupyter Notebook"
    path = Path(os.path.dirname(__file__)) / "test_files" / "nb.ipynb"

    fh = tmpdir.join("notebook.ipynb")
    with open(path) as f:
        fh.write(f.read())
    filename = os.path.join( fh.dirname, fh.basename )
    return filename

@pytest.fixture#(scope="module")
def notebook_file_simple(tmpdir):
    
    path = Path(os.path.dirname(__file__)) / "test_files" / "nb_simple.ipynb"

    fh = tmpdir.join("notebook.ipynb")
    with open(path) as f:
        fh.write(f.read())
    filename = os.path.join( fh.dirname, fh.basename )
    return filename

@pytest.fixture#(scope="module")
def notebook_file_empty(tmpdir):
    
    path = Path(os.path.dirname(__file__)) / "test_files" / "nb_empty.ipynb"

    fh = tmpdir.join("notebook.ipynb")
    with open(path) as f:
        fh.write(f.read())
    filename = os.path.join( fh.dirname, fh.basename )
    return filename

@pytest.fixture#(scope="module")
def notebook_file_with_tags(tmpdir):
    # TODO
    path = Path(os.path.dirname(__file__)) / "test_files"  / "nb_with_tags.ipynb"

    fh = tmpdir.join("notebook.ipynb")
    with open(path) as f:
        fh.write(f.read())
    filename = os.path.join( fh.dirname, fh.basename )
    return filename

@pytest.fixture#(scope="module")
def notebook_file_prerun(tmpdir):
    # TODO
    path = Path(os.path.dirname(__file__)) / "test_files"  / "nb_prerun.ipynb"

    fh = tmpdir.join("notebook.ipynb")
    with open(path) as f:
        fh.write(f.read())
    filename = os.path.join( fh.dirname, fh.basename )
    return filename

@pytest.fixture#(scope="module")
def notebook_file_unrun(tmpdir):
    # TODO
    path = Path(os.path.dirname(__file__)) / "test_files"  / "nb_unrun.ipynb"

    fh = tmpdir.join("notebook.ipynb")
    with open(path) as f:
        fh.write(f.read())
    filename = os.path.join( fh.dirname, fh.basename )
    return filename

@pytest.fixture#(scope="module")
def notebook_file_with_error(tmpdir):
    # TODO
    path = Path(os.path.dirname(__file__)) / "test_files"  / "nb_with_error.ipynb"

    fh = tmpdir.join("notebook.ipynb")
    with open(path) as f:
        fh.write(f.read())
    filename = os.path.join( fh.dirname, fh.basename )
    return filename

@pytest.fixture#(scope="module")
def notebook_file_with_outputs(tmpdir):
    # TODO
    path = Path(os.path.dirname(__file__)) / "test_files"  / "nb_with_outputs.ipynb"

    fh = tmpdir.join("notebook.ipynb")
    with open(path) as f:
        fh.write(f.read())
    filename = os.path.join( fh.dirname, fh.basename )
    return filename

@pytest.fixture
def notebook_file_task(tmpdir):
    # TODO
    path = Path(os.path.dirname(__file__)) / "test_files"  / "nb_task.ipynb"

    fh = tmpdir.join("notebook.ipynb")
    with open(path) as f:
        fh.write(f.read())
    filename = os.path.join( fh.dirname, fh.basename )
    return filename