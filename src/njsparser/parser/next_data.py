import orjson
from typing import Any

from ..utils import _supported_tree, make_tree

def get_next_data(value: _supported_tree) -> dict[str, Any]:
    """Returns the dict content of the `<script id='__NEXT_DATA__'>`, if it exists.

    Args:
        value (_supported_tree): The page to get the value from.

    Returns:
        dict[str, Any] | None: The dict content of the script, if there is, otherwise
            None.
    """
    if len(nextdata := make_tree(value=value).xpath("//script[@id='__NEXT_DATA__']/text()")):
        assert len(nextdata) == 1, f"invalid {len(nextdata)=}"
        return orjson.loads(nextdata.pop().strip())
    
def has_next_data(value: _supported_tree):
    """Tells if the given page contains a `<script id='__NEXT_DATA__'>`.

    Args:
        value (_supported_tree): The page to check for.

    Returns:
        bool: True if it contain any `__NEXT_DATA__` script, otherwise, False.
    """
    return get_next_data(value=value) is not None