


def output_match(output, output_types=None, mimetypes=None):
    return all((
        output_is_type(output, output_types=output_types),
        output_is_mimetype(output, mimetypes=mimetypes)
    ))

def output_is_type(output, output_types=None):
    # https://readthedocs.org/projects/nbformat/downloads/pdf/latest/
    if output_types is None:
        return True
    elif isinstance(output_types, str):
        return [output_types]
    return output["output_type"] in output_types 

def output_is_mimetype(output, mimetypes=None):
    if mimetypes is None:
        return True
    elif isinstance(mimetypes, str):
        return [mimetypes]

    if output_is_type(output, "display_data"):
        return output["data"] in mimetypes
    else:
        return False


# Extra 

def is_stream(output):
    return output_is_type(output, output_types=["stream"])

def is_display_data(output):
    return output_is_type(output, output_types=["display_data"])

def is_error(output):
    return output_is_type(output, output_types=["error"])

def is_execute_result(output):
    return output_is_type(output, output_types=["execute_result"])