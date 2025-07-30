import re
from typing import Union
from dataclasses import dataclass

from bs4 import BeautifulSoup
from markdown_it import MarkdownIt


STRUCTURAL_LINE_RE = re.compile(r'^(\s*[-*+]\s+|\s*\d+\.\s+|\|.+\||>\s*)')


@dataclass
class Section:
    """
    Represents a single section of the Markdown document.
    Contains its title, header level, location in the original text, and raw content.
    """
    title: str
    level: int
    start: int
    end: int
    content: str


@dataclass
class Node:
    """
    Represents a node in the hierarchical section tree.
    Holds the section title, header level, parsed content, and nested subsections.
    """
    title: str
    level: int
    parsed: Union[dict, list, str]
    subsections: list


def get_md_soup(text: str) -> BeautifulSoup:
    """
    Converts a Markdown text block into HTML and parses it into a BeautifulSoup object.
    """
    md_parser = MarkdownIt()
    md_parser.enable("table")  # Enables markdown table parsing
    md_parser.enable("code")   # Enables markdown code parsing
    html = md_parser.render(text)
    return BeautifulSoup(html, 'html.parser')


def is_single_tag_block(soup, tag_name: str) -> bool:
    """
    Check if the block consists of a single top-level tag (e.g. <table>, <ul>)
    with no other sibling tags.
    """
    tags = soup.find_all(recursive=False)
    return len(tags) == 1 and tags[0].name == tag_name


def is_structural_line(line: str) -> bool:
    """
    Returns True if the line is a Markdown block element (list, table row, blockquote).
    """
    return bool(STRUCTURAL_LINE_RE.match(line))


def convert_value(value: str) -> Union[int, float, str]:
    """
    Convert a string to an int, float, or datetime object is possible, or return the original string.
    """
    try:
        value = value.strip()
        if value.isdigit():
            return int(value)
        elif '.' in value:
            return float(value)
        else:
            return value
    except (ValueError, AttributeError):
        return value
