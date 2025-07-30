import re
from .utils import Section, Node
from .content_parser import parse_content_block


def split_sections(text: str):
    """
    Splits the Markdown text into Section objects.
    Each section is identified by a header (e.g., #, ##, ###).
    """
    pattern = re.compile(r'^(?P<header>#+) (?P<title>[^\n]+)', re.MULTILINE)
    matches = list(pattern.finditer(text))

    sections = []
    for i, match in enumerate(matches):
        # Calculate the 'end' of the current section:
        # It's the start of the next header or the end of the document.
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        sections.append(Section(
            title=match.group('title').strip(),    # The section's title text
            level=len(match.group('header')),      # The number of # symbols indicates nesting level
            start=match.start(),                   # Position where this header starts in the text
            end=end,                               # Position where this section's content ends
            content=text[match.end():end].strip()  # The actual text content of this section (excluding header)
        ))

    return sections


def build_section_tree(sections):
    """
    Builds a hierarchical tree of Nodes from the list of Section objects.
    Uses a stack to track the current section hierarchy.
    """
    root = Node(title='Root', level=0, parsed={}, subsections=[])
    stack = [root]

    for section in sections:
        node = Node(
            title=section.title,
            level=section.level,
            parsed=parse_content_block(section.content),
            subsections=[]
        )

        # Find the correct parent in the hierarchy
        while stack and stack[-1].level >= section.level:
            stack.pop()

        # Add this node as a child of the current parent
        parent_node = stack[-1]
        parent_node.subsections.append(node)

        # Push this node to the stack (might have its own children)
        stack.append(node)

    return root.subsections
