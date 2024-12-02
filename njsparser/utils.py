from lxml import etree
import logging

logger = logging.getLogger("njsparser")

_supported_tree = etree._Element | str | bytes
def make_tree(value: _supported_tree):
    """Returns an lxml etree for the give str or bytes, and returns
    the etree if the given argument is already one.

    Args:
        value (_supported_tree): Str or bytes html page, or an etree.

    Raises:
        TypeError: The tree isn't a string, bytes or etree.

    Returns:
        etree._Element: The tree.
    """
    if isinstance(value, etree._Element):
        return value
    elif isinstance(value, (str, bytes)):
        return etree.HTML(value)
    else:
        raise TypeError( 'waited a `str`, `bytes` or `etree._Element`, '
                         'got `%s`' % type(value).__name__ )
