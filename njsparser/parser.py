from lxml import etree
import orjson
import re
import typing

from .utils import make_tree, _supported_tree

__all__ = (
    "NextJsElement",
    "list_to_dict",
    "parse_nextjs_from_elements",
    "has_nextjs",
    "parse_nextjs_from_tree",
    "parse_nextjs_from_text",
)

NEXTJS_CLASSES = typing.Literal[None, "E", "HL", "I", "T"]
"""NextJS classes that I know of"""

_re_line = re.compile(r'^\s*self\.__next_f\.push\((\[\d+,\s*.+\])\)\s*$')
def find_nextjs_elements(value: _supported_tree):
    """Finds and strips the values of the nextjs elements found in the given tree.

    Args:
        value (_supported_tree): The tree.

    Returns:
        list[str]: Raw js data.
    """
    tree = make_tree(value=value)
    result: list[str] = []
    for item in tree.xpath('//script/text()'):
        if is_matching := _re_line.match(item):
            integer, content = orjson.loads(is_matching.groups()[0])
            content = typing.cast(str, content)
            if integer == 1:
                result.append(content)
    return result

class NextJsElement(typing.TypedDict):
    """The dict storing the nextjs elements."""
    value: str | None | list | dict
    """The value of the element."""
    value_class: str | None
    """The class of the element."""
    index: int
    """The index of the element."""

    @classmethod
    def from_parsing(cls, value: str, value_class: str, index: int) -> typing.Self:
        """Generate a NextJsElement from a parsing.

        Args:
            value (str): The string value.
            value_class (str): The class of the value.
            index (int): The index the value was declared at.

        Returns:
            NextJsElement: The obj.
        """
        return cls(
            value=orjson.loads(value) if value_class != "T" else value,
            value_class=value_class or None,
            index=index,
        )
    
def list_to_dict(l: list[NextJsElement]) -> dict[int, NextJsElement]:
    """Turns a list of NextJsElement to a dict like `{NextJsElement.index: NextJsElement}`

    Args:
        l (list[NextJsElement]): The list of NextJsElement.

    Returns:
        dict[int, NextJsElement]: The dict with index values of the `NextJsElement` as keys.
    """
    return {item["index"]: item for item in l}
    
_split_points = re.compile(rb"(?<!\\)\n[a-f0-9]+:")
def parse_nextjs_from_elements(
    elements: list[str],
    *,
    classes_filter: list[NEXTJS_CLASSES] = None,
):
    """Parses a list of nextjs elements.

    Args:
        elements (list[str]): The list of nextjs elements, as string (string content of\
            the script tag, without the `self.__next_f.push([1, ` prefix and the `])` suffix).
        classes_filter (list[NEXTJS_CLASSES], optional): A list of classes you only want to get returned.\
            The rest gets filtered out. The classes are `E`, `HL`, `I`, ... .Defaults to None, won't\
            filter out anything.

    Returns:
        list[NextJsElement]: The list of results.
    """
    if classes_filter is not None:
        assert isinstance(classes_filter, list) and \
            all([item is None or isinstance(item, str) for item in classes_filter])
    assert elements is not None, "`elements` argument is None"
    string = "".join(elements).encode()
    result: list[NextJsElement] = []

    pos = 0
    while True:
        index_string_end = string.find(b":", pos)
        index_string_raw = string[pos:index_string_end]
        if index_string_raw:
            index = int(index_string_raw, 16)
            pos = index_string_end + 1
        else:
            break

        value_class = ""
        while (char := chr(string[pos])).isalpha() and char.isupper():
            value_class += char
            pos += 1
        value_class = value_class or None
        
        if value_class == "T":
            text_length_string_end = string.find(b",", pos)
            text_length_hex = string[pos:text_length_string_end]
            text_length = int(text_length_hex, 16)
            text_start = text_length_string_end + 1 # (+1 for the comma)
            value = string[text_start:text_start+text_length]
            pos = text_start + text_length
        else:
            try:
                data_end = next(_split_points.finditer(string=string, pos=pos)).start()
                value = string[pos:data_end]
                pos = data_end + 1
            except StopIteration:
                value = string[pos:-1]
                pos += len(value)

        if classes_filter is None or value_class in classes_filter:
            result.append(NextJsElement.from_parsing(value=value.decode(), value_class=value_class, index=index))

    return result

def has_nextjs(value: _supported_tree):
    """Does the text/tree contains any nextjs data ?

    Args:
        value (str | etree._Element): The text/tree to check in for any nextjs data.

    Returns:
        bool: If `return_elements` is `False` / `None`.
    """
    try:
        next(find_nextjs_elements(value=value))
        return True
    except StopIteration:
        return False

def parse_nextjs_from_tree(
    tree: etree._Element,
    *,
    classes_filter: list[NEXTJS_CLASSES] = None,
):
    """Parses a list of nextjs elements.

    Args:
        tree (etree._Element): The tree to parse nextjs from.
        classes_filter (list[NEXTJS_CLASSES], optional): A list of classes you only want to get returned.\
            The rest gets filtered out. The classes are `E`, `HL`, `I`, ... .Defaults to None, won't\
            filter out anything.

    Returns:
        - None: If the given tree doesn't contain any nextjs data.
        - list[NextJsElement]: The list of results.
    """
    assert isinstance(tree, etree._Element)
    if elements := find_nextjs_elements(value=tree):
        return parse_nextjs_from_elements(elements=elements, classes_filter=classes_filter)

def parse_nextjs_from_text(
    text: str,
    *,
    classes_filter: list[NEXTJS_CLASSES] = None,
):
    """Parses a list of nextjs elements.

    Args:
        text (str): The raw html string to parse nextjs from.
        classes_filter (list[NEXTJS_CLASSES], optional): A list of classes you only want to get returned.\
            The rest gets filtered out. The classes are `E`, `HL`, `I`, ... .Defaults to None, won't\
            filter out anything.

    Returns:
        list[NextJsElement]: The list of results.
    """
    assert isinstance(text, (str, bytes))
    return parse_nextjs_from_tree(tree=etree.HTML(text=text), classes_filter=classes_filter)

parse_nextjs_from_bytes = parse_nextjs_from_text