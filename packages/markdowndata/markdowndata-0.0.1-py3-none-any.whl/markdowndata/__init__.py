from .process_markdown import MarkDataParser

def load(file):
    parser = MarkDataParser()
    parser.load(file.name)
    return parser.data