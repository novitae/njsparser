from lxml import etree
import ujson
import re
import typing

__all__ = ( "NEXTJS_CLASSES", "find_nextjs_elements", "NextJsElement", "parse_nextjs_from_elements", "has_nextjs",
            "parse_nextjs_from_tree", "parse_nextjs_from_text", "list_to_dict", )

NEXTJS_CLASSES = typing.Literal[None, "E", "HL", "I", "T"]
"""NextJS classes that I know of"""

_namespaces = {'re': 'http://exslt.org/regular-expressions'}
def find_nextjs_elements(tree: etree._Element) -> list[str]:
    """Finds and strips the values of the nextjs elements found in the given tree.

    Args:
        tree (etree._Element): The page under an `lxml.etree.HTML(text=...)` obj.

    Returns:
        list[str]: The list of elements.
    """
    return [
        ujson.loads(item.text.strip().removeprefix("self.__next_f.push([1, ").removesuffix("])"))
        for item in tree.xpath(
            './/script[re:match(text(), $pattern)]',
            namespaces=_namespaces,
            pattern='self\.__next_f\.push\(\[1, (".*"|null)\]\)'
        )
    ]

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
            value=ujson.loads(value) if value_class != "T" else value,
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
    
_split_points = re.compile(r"(?<!\\)\n[a-f0-9]+:")
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
    assert elements is not None, "`elements` argument is None"
    string = "".join(elements)
    result: list[NextJsElement] = []

    pos = 0
    while True:
        index_string_end = string.find(":", pos)
        index_string_raw = string[pos:index_string_end]
        if index_string_raw:
            index = int(index_string_raw, 16)
            pos = index_string_end + 1
        else:
            break

        value_class = ""
        while (char := string[pos]).isalpha() and char.isupper():
            value_class += char
            pos += 1
        
        if value_class == "T":
            text_length_string_end = string.find(",", pos)
            text_length = int(string[pos:text_length_string_end], 16)
            text_start = text_length_string_end + 1
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
            result.append(NextJsElement.from_parsing(value=value, value_class=value_class, index=index))

    return result

@typing.overload
def has_nextjs(value: str | etree._Element, *, return_elements: typing.Literal[True] = None) -> tuple[bool, list[str] | None]:
    ...

@typing.overload
def has_nextjs(value: str | etree._Element, *, return_elements: typing.Literal[False] = None) -> bool:
    ...

def has_nextjs(value: str | etree._Element, *, return_elements: bool = None):
    """Does the text/tree contains any nextjs data ?

    Args:
        value (str | etree._Element): The text/tree to check in for any nextjs data.
        return_elements (bool, optional): Do we return the elements we might have found ? Might be\
            useful to directly run `parse_nextjs_from_elements` from them. Defaults to None (False).

    Raises:
        TypeError: The value isn't a `str` neither an `etree._Element`.

    Returns:
        - tuple[bool, list[str] | None]: If `return_elements` is `True`.
        - bool: If `return_elements` is `False` / `None`.
    """
    if isinstance(value, str):
        tree = etree.HTML(text=value)
    elif isinstance(tree, etree._Element) is False:
        raise TypeError('waited a `str` or `etree._Element`, got `%s`' % type(tree).__name__)
    elements = find_nextjs_elements(tree=tree)
    has_elements = bool(elements)
    if return_elements:
        return has_elements, elements or None
    else:
        return has_elements
            
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
    if elements := find_nextjs_elements(tree=tree):
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
    return parse_nextjs_from_tree(tree=etree.HTML(text=text), classes_filter=classes_filter)