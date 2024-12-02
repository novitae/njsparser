from typing import List, Union
import orjson
import re
import base64

from ..utils import make_tree, _supported_tree

_raw_f_data = List[Union[list[int], list[int, str]]]
_re_f_init = re.compile(r'\(self\.__next_f\s?=\s?self\.__next_f\s?\|\|\s?\[\]\)\.push\((\[.+)\)')
_re_f_payload = re.compile(r'self\.__next_f\.push\((\[.+)\)$')
def has_flight_data(value: _supported_tree) -> bool:
    """Tells if a given page contains any flight data.

    Args:
        value (_supported_tree): The page to check for.

    Returns:
        bool: True if the page contains any flight data.
    """
    scripts = make_tree(value=value).xpath(f'.//script/text()')
    return any([_re_f_init.match(script) for script in scripts])

def get_raw_flight_data(value: _supported_tree) -> _raw_f_data | None:
    result = []
    # The var `result` would be the array shown when doing `self.__next_f`
    # on a page that contains flight data.
    found_init = False
    for script in make_tree(value=value).xpath('.//script/text()'):
        script: str = script.strip()
        if found_init is False and (flight_data_init_match := _re_f_init.match(script)):
            found_init = True
            result.append(orjson.loads(flight_data_init_match.groups()[0]))
        if is_matching := _re_f_payload.match(script):
            result.append(orjson.loads(is_matching.groups()[0]))
    return result or None

# https://chatgpt.com/share/674e2a5c-6a34-8007-a1f7-510a74d89d26
# https://github.com/vercel/next.js/blob/5405f66fc78d02cc30afd0284630d91f676c3f38/packages/next/src/client/app-index.tsx#L43-L80
def decode_raw_flight_data(flight_data: _raw_f_data) -> List[Union[str, bytes]]:
    initial_server_data_buffer = None
    initial_form_state_data = None # Idk what is this for.
    for seg in flight_data:
        if seg[0] == 0:  # Bootstrap segment
            initial_server_data_buffer = []
        elif seg[0] == 1:  # Partial text response
            if initial_server_data_buffer is None:
                raise Exception("Var `initial_server_data_buffer` not yet a list.")
            initial_server_data_buffer.append(seg[1])
        elif seg[0] == 2:  # Form state
            initial_form_state_data = seg[1]
        elif seg[0] == 3:  # Binary data
            if initial_server_data_buffer is None:
                raise Exception("Var `initial_server_data_buffer` not yet a list.")
            decoded_chunk = base64.b64decode(seg[1].encode())
            initial_server_data_buffer.append(decoded_chunk)
        else:
            raise KeyError(f'Unknown segment type {seg[0]=}')
    return initial_server_data_buffer

# def get_flight_data(value: _supported_tree) -> dict[str, Any] | None:
#     """Returns the flight data of a given page.

#     Args:
#         value (_supported_tree): The page to the raw flight data from.

#     Returns:
#         dict[str, Any]: The raw
#         None: There is not flight data in the given page.
#     """
#     if (raw_flight_data := get_raw_flight_data(value=value)) is not None:
#         return orjson.loads(raw_flight_data)
    
# https://github.com/vercel/next.js/blob/5405f66fc78d02cc30afd0284630d91f676c3f38/packages/next/src/client/app-index.tsx#L43-L80