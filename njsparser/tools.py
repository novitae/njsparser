import re

from .utils import _supported_tree
from .parser import has_next_data, has_flight_data

def has_nextjs(value: _supported_tree):
    """Tells if the page has some nextjs data in it.

    Args:
        value (_supported_tree): The page to check for.

    Returns:
        bool: True if it contains any nextjs data, otherwise, False.
    """
    return any([has_next_data(value=value), has_flight_data(value=value)])

_re_build_id = re.compile(r"^[A-Za-z\d\-_]{21}$")

# def find_build_id(value: _supported_tree):
#     """Searches and return (or not) the build id of the given page.

#     Args:
#         value (_supported_tree): The page to find the build id from.
#     """
#     tree = make_tree(value=value)
#     if (next_data := get_next_data(value=tree)) is not None:
#         try:
#             return next_data["buildId"]
#         except KeyError:
#             logger.warning( "Found a next_data dict in the page, " \
#                             "but did't contain any `buildId` key." )
#     elif (found_next_elements := find_nextjs_elements(value=tree)):
#         for parsed_nextjs_item in parse_nextjs_from_elements(elements=found_next_elements):
#             ""