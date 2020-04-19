
import pytest
import os
from pathlib import Path

@pytest.fixture
def notebook_folder():
    return str(Path(os.path.dirname(__file__)) / "test_files")