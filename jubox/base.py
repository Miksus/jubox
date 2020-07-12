

import nbformat

import copy

from jubox.utils.html import get_css

class JupyterObject:
    """
    Base class for Jubox classes
    """

    nb_version = 4
    kernel_name = "python3"

    @classmethod
    def _get_nb_format(cls):
        "Get nbformat subpackage of given version"
        return getattr(nbformat, f"v{cls.nb_version}")

    def __copy__(self):
        # https://stackoverflow.com/a/15774013/13696660
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        # https://stackoverflow.com/a/15774013/13696660
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result

    @staticmethod
    def get_css():
        "Get CSS used in Jupyter Notebooks"
        return get_css()