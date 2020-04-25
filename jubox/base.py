

import nbformat

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