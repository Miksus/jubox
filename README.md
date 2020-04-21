
# JuBox
[![Build Status](https://travis-ci.com/Miksus/jubox.svg?branch=master)](https://travis-ci.com/Miksus/jubox)

> Programmatical Jupyter Notebook API for humans

> Jupyter Notebook extension, Python 3, Easy to use


---

![Example](docs/img/example.png "Rain Simulation")

## What?
- Pythonic approach to load, modify, run and save Jupyter Notebooks in Python code
- This enables to quickly and easily create:
    - Parametrized notebooks
    - Version controlable notebooks directly from inserted code snippets, Python files or even straight from Python functions and classes.
    - Notebooks with code generated markdown

## Installation

- Pip install from pip
```shell
pip install jubox
```

- Clone the source code and pip install:
```shell
git clone https://github.com/Miksus/jubox.git
cd jubox
pip install -e .
```

## Example

```python
from jubox import JupyterNotebook, JupyterCell

# Load jupyter Notebook
nb = JupyterNotebook("my_file.ipynb")
nb.load()

# Run the notebook
# by making a copy (output is lost if raised exception)
nb_runned = nb()

# or in place (maintains exceptions in the file)
nb(inplace=True)


# save the file to the original file
nb.save()
# or to new file
nb.to_ipynb("run_notebook.ipynb")

# or to HTML
nb.to_html("run_notebook.html")

# or to Python file
nb.to_python("notebook_code.py")


# Get cells with specific tags
param_cells = nb.get_cells(tags=["parametrized"])

# Rewrite the first tagged cell with dict of parameters
new_cell = JupyterCell.from_variable_dict(run_date="2020-01-01", category="blue")
param_cells[0].overwrite(new_cell, inplace=True)

```


---

## Features
- Convenient object oriented API for Jupyter Notebooks. 
- Load, save and run notebooks and get cells containing 
- Render Jupyter Notebooks in a Jupyter Notebook!

## Test
Pytest was chosen as testing suites. Tests are found in test directory. 

---

## Author

* **Mikael Koli** - [Miksus](https://github.com/Miksus) - koli.mikael@gmail.com

---
## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**