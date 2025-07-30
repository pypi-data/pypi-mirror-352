import re
import yaml

from .utils import convert_value, get_md_soup, is_single_tag_block, is_structural_line


def detect_value_type(text: str) -> str | None:
    """
    Detect the type of content block (YAML, table, list, or text).
    Only classifies as md_table or md_list if the content is *only* that structure.
    """
    text = text.strip()
    if not text:
        return None

    # YAML detection (delimited by ===)
    if re.search(r'===\s*\n(.*?)\n===', text, re.DOTALL):
        return 'yaml_dict'

    # Convert markdown to HTML
    soup = get_md_soup(text)

    # Check for exactly one <table> and no other tags or text
    if soup.find('table') and is_single_tag_block(soup, 'table'):
        return 'md_table'

    # Check for exactly one <ul> and no other tags or text
    if soup.find('ul') and is_single_tag_block(soup, 'ul'):
        return 'md_list'

    # Fallback: process everything as Markdown text
    return 'md_text'


def yaml_dict_parser(text: str) -> dict:
    """
    Parse YAML from a string (surrounded by ===) and returns it as a dictionary.
    Assumes YAML is a block at the beginning of the text.
    """
    match = re.search(r'===\s*\n(.*?)\n===', text, re.DOTALL)
    if match:
        yaml_data = yaml.safe_load(match.group(1))
        if yaml_data:
            return {k: convert_value(v) for k, v in yaml_data.items()}
    return {}


def md_table_parser(text: str) -> list[dict]:
    """
    Parse a Markdown table and returns it as a list of dictionaries.
    Assumes the markdown is converted to HTML with <table> elements.
    """
    soup = get_md_soup(text)
    table = soup.find('table')
    if not table:
        return []

    # Extract headers and row data
    headers = [th.get_text(strip=True) for th in table.find_all('th')]
    rows = []
    for tr in table.find_all('tr')[1:]:  # Skip header row
        cells = [convert_value(td.get_text(strip=True)) for td in tr.find_all(['td', 'th'])]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))

    return rows


def md_list_parser(text: str) -> list:
    """
    Parse a Markdown list and returns it as a list of values.
    Assumes the markdown is converted to HTML with <ul> elements.
    """
    soup = get_md_soup(text)
    ul = soup.find('ul')
    if not ul:
        return []
    return [convert_value(li.get_text(strip=True)) for li in ul.find_all('li')]


def md_text_parser(text: str) -> str:
    """
    Parse Markdown text by:
    - Joining lines separated by a single newline (soft breaks)
    - Preserving formatting (bold, italic, headers, code, code block, etc.)
    - Preserving paragraph breaks (double or more newlines)
    - Preserving fenced code blocks exactly
    """
    process_text = process_code_blocks(text, process_soft_breaks)
    return convert_value(process_text)


def process_code_blocks(text: str, non_code_callback) -> str:
    """
    Process Markdown text, preserving fenced code blocks and applying a transformation
    only to the non-code sections using `non_code_callback`.
    """
    code_pattern = re.compile(r'```.*?```', re.DOTALL)
    result = []
    last_end = 0

    for match in code_pattern.finditer(text):
        start, end = match.span()
        non_code_part = text[last_end:start]
        code_block = match.group()

        if non_code_part.strip():
            result.append(non_code_callback(non_code_part))
        result.append(code_block)

        last_end = end

    remaining = text[last_end:]
    if remaining.strip():
        result.append(non_code_callback(remaining))

    return '\n\n'.join(result)


def process_soft_breaks(text: str) -> str:
    """
    Joins lines separated by a single newline, except for Markdown block elements:
    - Lists
    - Tables
    - Blockquotes
    Preserves paragraph breaks (2+ newlines).
    """
    lines = text.split('\n')
    processed = []
    paragraph_lines = []

    for line in lines:
        if line.strip() == '':
            if paragraph_lines:
                processed.append(' '.join(paragraph_lines))
                paragraph_lines = []
            processed.append('')
            continue

        if is_structural_line(line):
            if paragraph_lines:
                processed.append(' '.join(paragraph_lines))
                paragraph_lines = []
            processed.append(line)
        else:
            paragraph_lines.append(line.strip())

    if paragraph_lines:
        processed.append(' '.join(paragraph_lines))

    return '\n'.join(processed)


def parse_content_block(text: str):
    """
    Parse a given block of Markdown text into structured data.
    Automatically detects the content type (YAML, table, list, text) and
    dispatches to the appropriate parser. Raises an error if the content
    cannot be parsed or returns an empty result.
    """
    text = text.strip()
    if not text:
        return {}

    v_type = detect_value_type(text)
    if not v_type:
        raise ValueError(f'No parser found for content: {text}')

    parser_functions = {
        'yaml_dict': yaml_dict_parser,
        'md_table': md_table_parser,
        'md_list': md_list_parser,
        'md_text': md_text_parser
    }

    parser = parser_functions[v_type]
    value = parser(text)
    if not value:
        raise ValueError(f'Parser for {v_type} returned empty value for: {text}')
    return value
