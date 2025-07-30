from .process_markdown import MarkDataParser


def loads(text):
    parser = MarkDataParser()
    return parser.loads(text)


def load(file):
    return loads(file.read())