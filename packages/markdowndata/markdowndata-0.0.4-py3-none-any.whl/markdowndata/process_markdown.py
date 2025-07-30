from typing import Union, List, IO
from .section_tree import split_sections, build_section_tree
from .utils import Node


class MarkDataParser:
    """
    Parses a Markdown document into a JSON-like dictionary structure.
    Builds a hierarchy of sections and converts each section's content into a structured form.
    """
    def __init__(self):
        self.data = {}

    def loads(self, text: str) -> dict:
        """
        Loads markdown content from a file path or file-like object, parses it,
        and builds a nested dictionary of structured data.
        """
        # Split the text into Section objects based on markdown headers
        sections = split_sections(text)

        # Build a hierarchical tree of sections and subsections
        section_tree = build_section_tree(sections)

        # Convert the section tree into a JSON-like dictionary structure
        self.data = self.build_dict(section_tree)
        return self.data

    def build_dict(self, sections: List[Node]) -> dict:
        """
        Recursively converts a list of Node objects into a JSON-like dictionary structure.
        """
        result = {}
        for node in sections:
            sub_dict = self.build_dict(node.subsections)

            if isinstance(node.parsed, dict):
                # If the parsed content is a dictionary, merge it with its subsections
                merged = {**node.parsed, **sub_dict}
            elif node.subsections:
                # If subsections exist but parsed content is not a dict,
                # wrap both into a new dictionary
                merged = {
                    'content': node.parsed,
                    **sub_dict
                } if node.parsed else sub_dict
            else:
                # If no subsections, return the parsed content (could be string, list, or None)
                merged = node.parsed

            # Use the node's title as the key in the dictionary
            result[node.title] = merged
        return result
