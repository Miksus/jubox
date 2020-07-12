
from . import code
from jubox.utils.outputs import (
    output_match, 
    output_to_plain, output_to_html,
    is_stream, is_display_data, is_error, is_execute_result
)

@code.register_accessor("outputs")
class Outputs:

    def __init__(self, cell):
        self._cell = cell

    def get(self, **kwargs):
        return [
            output
            for output in self
            if output_match(output, **kwargs)
        ]

    @property
    def errors(self):
        return [
            output
            for output in self
            if is_error(output)
        ]

    @property
    def execute_results(self):
        return [
            output
            for output in self
            if is_execute_result(output)
        ]

    @property
    def streams(self):
        return [
            output
            for output in self
            if is_stream(output)
        ]

    @property
    def display_data(self):
        return [
            output
            for output in self
            if is_display_data(output)
        ]

    def as_html(self, use_css=True, include_css=False):
        """Turn the cell outputs to HTML (ignores those that cannot be converted)
        
        Arguments:
        ----------
            use_css {bool} : Whether to use CSS classes (in errors). Otherwise is without colors
            include_css {bool} : Whether to include the Jupyter Notebook CSS to the HTML
        """
        outputs = self.streams + self.execute_results + self.errors + self.display_data
        
        html = '\n'.join([
            output_to_html(output, use_css=use_css)
            for output in outputs
        ])

        if include_css:
            html = f"<style>{self.get_css()}</style>\n" + html
        return html
        
    def as_plain(self):
        outputs = self.streams + self.execute_results + self.errors + self.display_data
        return '\n'.join([
            output_to_plain(output)
            for output in outputs
        ])

    def __iter__(self):
        for output in self._cell["outputs"]:
            yield output

    def __len__(self):
        return len(self._cell["outputs"])

    def __set__(self, instance, value):
        self._cell["outputs"] = value

    def __delete__(self, instance):
        self._cell["outputs"] = []


    def __getitem__(self, item):
        return self._cell["outputs"][item]

    def __setitem__(self, item, val):
        "Set outputs in the cell"
        self._cell["outputs"][item] = val

    def __delitem__(self, item):
        "Delete an output"
        del self._cell["outputs"][item]