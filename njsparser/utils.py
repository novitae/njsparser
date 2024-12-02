from lxml import etree
import logging

logger = logging.getLogger("njsparser")

_supported_tree = etree._Element | str | bytes
def make_tree(value: _supported_tree):
    """Makes an lxml Element if you feed bytes or str, returns
    the Element if you feed an Element.

    Args:
        value (_supported_tree): The potential tree.

    Raises:
        TypeError: The tree isn't a string, bytes or etree._Element.

    Returns:
        etree._Element: The tree
    """
    if isinstance(value, etree._Element):
        return value
    elif isinstance(value, (str, bytes)):
        return etree.HTML(value)
    else:
        raise TypeError('waited a `str`, `bytes` or `etree._Element`, got `%s`' % type(value).__name__)
