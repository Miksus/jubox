
from nbconvert.preprocessors import CSSHTMLHeaderPreprocessor

def get_css(config_dir=None):

    # See: https://github.com/jupyter/nbconvert/blob/master/nbconvert/preprocessors/csshtmlheader.py

    if config_dir is None:
        config_dir = "" # This should not be found
    processor = CSSHTMLHeaderPreprocessor()
    _, resources = processor.preprocess(None, {"config_dir": config_dir})
    css = resources["inlining"]["css"]
    
    return css

    