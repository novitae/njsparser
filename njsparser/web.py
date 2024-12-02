"soon inshallah"
# import re
# import orjson

# from .utils import _supported_tree, make_tree, logger
# from .parser import find_nextjs_elements, parse_nextjs_from_elements, list_to_dict

# _re_build_id = re.compile(r"^[A-Za-z\d\-_]{21}$")

# # https://nextjs.org/_next/static/qT7EZ7qtY5x8nLheXTfUs/_buildManifest.js

# def find_next_data(value: _supported_tree):
#     """Searches and return (or not) the content of the `<script id='__NEXT_DATA__'>`
#     in the given page.

#     Args:
#         value (_supported_tree): The page to search for the value in.

#     Raises:
#         AssertionError: We found more than 1 `__NEXT_DATA__` script.

#     Returns:
#         str: The content of the `__NEXT_DATA__` script.
#     """
#     tree = make_tree(value=value)
#     if (next_datas := tree.xpath("//script[@id='__NEXT_DATA__']/text()")):
#         assert (_ln := len(next_datas) == 1), f"Found more than 1 `__NEXT_DATA__` script ({_ln})"
#         return str(next_datas.pop())

# def find_build_id(value: _supported_tree):
#     """Searches and return (or not) the build id of the given page.

#     Args:
#         value (_supported_tree): The page to find the build id from.
#     """
#     tree = make_tree(value=value)
#     if (raw_next_data := find_next_data(value=tree)) is not None:
#         next_data = orjson.loads(raw_next_data)
#         try:
#             return next_data["buildId"]
#         except KeyError:
#             logger.warning( "Found a next_data dict in the page, " \
#                             "but did't contain any `buildId` key." )
#     elif (found_next_elements := find_nextjs_elements(value=tree)):
#         for parsed_nextjs_item in parse_nextjs_from_elements(elements=found_next_elements):
#             if parsed_nextjs_item["value_class"] is None and \
#                 isinstance(parsed_nextjs_item["value"], list) and \
#                 len(parsed_nextjs_item["value"]) == 4 and \
#                 parsed_nextjs_item["value"][0] == "$" and \
#                 parsed_nextjs_item["value"][1] == "$L1" and \
#                 parsed_nextjs_item["value"][2] is None:
#                 ""