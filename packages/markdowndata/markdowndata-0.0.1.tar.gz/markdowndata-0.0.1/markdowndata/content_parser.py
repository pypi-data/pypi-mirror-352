import re
import yaml

from .utils import convert_value, get_md_soup


def detect_value_type(text: str) -> str | None:
    """
    Detect the type of content block (YAML, table, list, or text).
    Returns the content type string or None if no match is found.
    """
    text = text.strip()
    if not text:
        return None

    # YAML detection (delimited by ---)
    if re.search(r'---\s*\n(.*?)\n---', text, re.DOTALL):
        return 'yaml_dict'

    # Convert markdown to HTML and analyze for tables, lists, or text
    soup = get_md_soup(text)
    if soup.find('table'):
        return 'md_table'
    elif soup.find('ul'):
        return 'md_list'
    elif soup.get_text(strip=True):
        return 'md_text'

    return None


def yaml_dict_parser(text: str) -> dict:
    """
    Parse YAML from a string (surrounded by ---) and returns it as a dictionary.
    Assumes YAML is a block at the beginning of the text.
    """
    match = re.search(r'---\s*\n(.*?)\n---', text, re.DOTALL)
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
    Parse a Markdown text block and return its text content as a string.
    Ensures lines flow together as a paragraph, not split across lines.
    """
    soup = get_md_soup(text)
    raw_text = soup.get_text(strip=True)
    return convert_value(' '.join(raw_text.splitlines()))


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
