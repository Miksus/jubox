
from nbconvert.filters import (
    wrap_text, ansi2html, html2text,
    indent, strip_ansi
)
from .match import is_stream, is_display_data, is_error, is_execute_result

def output_to_plain(output):
    if is_stream(output):
        return output["text"]

    elif is_display_data(output) or is_execute_result(output):
        data = output["data"]
        if "text/plain" in data:
            return data["text/plain"]
        elif "text/html" in data:
            # TODO: Implement
            return ""
        else:
            # Not implemented
            return ""

    elif is_error(output):
        traceback = '\n'.join(output["traceback"])
        return strip_ansi(traceback)

    else:
        return ""

def output_to_html(output, use_css=False):
    if is_stream(output):
        return text_to_html(output["text"])

    elif is_display_data(output) or is_execute_result(output):
        data = output["data"]
        if "text/html" in data:
            return data["text/html"]
        elif "text/plain" in data:
            return text_to_html(data["text/plain"])
        else:
            # Not implemented
            return ""

    elif is_error(output):
        if use_css:
            return ansi2html('\n'.join(output["traceback"])).replace("\n", "<br>")
        else:
            # TODO: Parse ansi to HTML color codes or parse the ansi2html css classes
            traceback = '<br>'.join(output["traceback"])
            return text_to_html(strip_ansi(traceback))

    else:
        return ""

def text_to_html(s):
    return s.replace("\n", "<br>")