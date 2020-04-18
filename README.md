
# JuBox

> Programmatical Jupyter Notebook API for humans

> Jupyter Notebook extension, Python 3, Easy to use


---

![Example](docs/img/example.png "Rain Simulation")

## Why?
- There is lacking a generic and obvious approach to handle Jupyter Notebooks in Python code. 
There are awesome tools, such as nbformat and nbconvert, but many of them are not easy to get into
and require modeate amount of reading docs to get anything done.
- Instead of scattering functionalities, everything is wrapped into a single class with all the
necessary functionalities.

## Example

```python
from jubox import JupyterNotebook

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
```

## Installation


- Clone or download the source code this repo to your local machine. Pip install coming when I have time.


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