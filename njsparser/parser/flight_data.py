"""Part of the lib to interract with the nextjs data located looking like `self.__next_f.push(1, "...")`"""

from typing import List, Union, TypeVar
import orjson
import re
import base64
from enum import Enum

from ..utils import make_tree, _supported_tree
from .types import resolve_type, Element, TE

_raw_f_data = List[Union[list[int], list[int, str]]]
_re_f_init = re.compile(r'\(self\.__next_f\s?=\s?self\.__next_f\s?\|\|\s?\[\]\)\.push\((\[.+?\])\)')
_re_f_payload = re.compile(r'self\.__next_f\.push\((\[.+)\)$')

def has_flight_data(value: _supported_tree) -> bool:
    """Tells if a given page contains any flight data.

    Args:
        value (_supported_tree): The page to check for.

    Returns:
        bool: True if the page contains any flight data.
    """
    scripts = make_tree(value=value).xpath('//script/text()')
    return any([_re_f_init.search(script) for script in scripts])

def get_raw_flight_data(value: _supported_tree) -> _raw_f_data | None:
    """Will return the raw flight data, under the same format as the array shown when
    doing `console.log(self.__next_f);` in the console of a website containing nextjs
    flight data.

    Args:
        value (_supported_tree): The page to get the data from.

    Returns:
        _raw_f_data | None: The `self.__next_f` array, or None if nothing found.
    """
    result, found_init = [], False
    for script in make_tree(value=value).xpath('//script/text()'):
        script: str = script.strip()
        if found_init is False and \
            (flight_data_init_match := _re_f_init.match(script)):
            found_init = True
            result.append(orjson.loads(flight_data_init_match.groups()[0]))
        if is_matching := _re_f_payload.match(script):
            result.append(orjson.loads(is_matching.groups()[0]))
    return result or None

class Segment(int, Enum):
    is_bootstrap = 0
    is_not_bootstrap = 1
    is_form_state = 2
    is_binary = 3

# https://chatgpt.com/share/674e2a5c-6a34-8007-a1f7-510a74d89d26
# https://github.com/vercel/next.js/blob/5405f66fc78d02cc30afd0284630d91f676c3f38/packages/next/src/client/app-index.tsx#L43-L80
def decode_raw_flight_data(raw_flight_data: _raw_f_data) -> List[str]:
    """Decodes the raw flight data the same way that the client would do it.

    Args:
        raw_flight_data (_raw_f_data): The raw flight data, coming from the
            output of `get_raw_flight_data(...)`, representing the array
            `self.__next_f` from a page that would contain flight data.

    Raises:
        KeyError: Unknown segment type.
        UnboundLocalError

    Returns:
        List[str]: The chunks of flight data.
    """
    try:
        for seg in raw_flight_data:
            if seg[0] == Segment.is_bootstrap:
                initial_server_data_buffer = []
            elif seg[0] == Segment.is_not_bootstrap:
                initial_server_data_buffer.append(seg[1])
            elif seg[0] == Segment.is_form_state:
                initial_form_state_data = seg[1]
            elif seg[0] == Segment.is_binary:
                decoded_chunk = base64.b64decode(seg[1].encode())
                initial_server_data_buffer.append(decoded_chunk.decode())
            else:
                raise KeyError(f'Unknown segment type {seg[0]=}')
    except UnboundLocalError as error:
        error.add_note( 'The `initial_server_data_buffer` was not yet initialized '
                        'and a segment tried to append its data to it. This should '
                        'not be happening if the flight data starts correctly with '
                        'a the `is_bootstrap` segment.' )
        raise error
    return initial_server_data_buffer

# TODO: update `parse_decoded_raw_flight_data` with the new data found in react at:
# https://github.com/facebook/react/blob/1c9b138714a69cd136a3d82769b1fd9a4b318953/packages/react-client/src/ReactFlightClient.js#L2874-L2993
# --> processFullBinaryRow()
#             \/
# --> processFullStringRow() -> str[0] == "H" -> resolveHint -> parseModel(str[1]) -> parseModel -> dispatchHint(JSON.parse(...), str[1])   -> str[1] == "D" -> prefetchDNS
#                            ->        == "I" -> resolveModule                                                                              ->        == "C" -> preconnect
#                            ->        == "E" -> JSON.parse(...).digest                                                                     ->        == "L" -> preload
#                            ->        == "T" -> resolveText                                                                                ->        == "m" -> preloadModule
#                            ->        == "D" -> resolveDebugInfo                                                                           ->        == "X" -> preinitScript
#                            ->        == "W" -> resolveConsoleEntry                                                                        ->        == "S" -> preinitStyle
#                            ->        == "R" -> startReadableStream                                                                        ->        == "M" -> preinitModuleScript
#                            ->        == "r" -> startReadableStream(bytes)
#                            ->        == "X" -> startAsyncIterable(false)
#                            ->        == "x" -> startAsyncIterable(true)
#                            ->        == "C" -> stopStream
#                            ->        == "P" -> resolvePostponeProd
#                            -> else          -> resolveModel


FD = dict[int, TE]

_split_points = re.compile(rb"(?<!\\)\n[a-f0-9]*:")
def parse_decoded_raw_flight_data(decoded_raw_flight_data: List[str]) -> FD:
    # Here we join, then encode the decoded raw flight data. It is important to encode
    # it, otherwise some values in string will take way more characters, and the text
    # size announced in `"T"` will not be pointing to the correct text end.
    compiled_raw_flight_data = "".join(decoded_raw_flight_data).encode()
    indexed_result, pos = {}, 0
    while True:
        # We find the position of the first `:`. If it is `-1`, it means we are at
        # the end of the data, nothing else to parse in the remaining at least, so
        # we break there. Otherwise we can determine the size of the index hex string
        # that is between the current pos and the found `:` pos, then parse it into
        # an actual int. Then update the pos to be right after the `:`.
        index_string_end = compiled_raw_flight_data.find(b":", pos)
        if index_string_end == -1:
            break
        index_string_raw = compiled_raw_flight_data[pos:index_string_end]
        if index_string_raw:
            index = int(index_string_raw, 16)
        else:
            index = None
        pos = index_string_end + 1

        # We iterate until the character is not alphabetic nor upper. This allows to
        # iterate only as long as we are on the class, since they look like `"HF"`,
        # `"I"`, `"T"`, ... . If the string is empty, we will set it to `None`.
        value_class = ""
        while (char := chr(compiled_raw_flight_data[pos])).isalpha() and char.isupper():
            value_class += char
            pos += 1
        value_class = value_class or None
        
        # If the class is `"T"`, if will right after it have the hex size of the text
        # it contains. It is then separated to the content with a `","`. We find the
        # comma, select the size hex string (`text_length_hex`), then turn it into an
        # `int`. Then we select the text with the size we just calculated.
        if value_class == "T":
            text_length_string_end = compiled_raw_flight_data.find(b",", pos)
            text_length_hex = compiled_raw_flight_data[pos:text_length_string_end]
            text_length = int(text_length_hex, 16)
            text_start = text_length_string_end + 1 # (+1 for the comma)
            raw_value = compiled_raw_flight_data[text_start:text_start+text_length].decode()
            pos = text_start + text_length
        
        # Otherwise, we will search for the next time we have a non escaped `"\n"`,
        # followed by the hex string of the index, with `":"` (using the regex
        # `_split_points`).
        else:
            # If we have a match, we select the position of the start of it, and will
            # use it as the end position of the current value.
            if data_end_match := _split_points.search(string=compiled_raw_flight_data, pos=pos):
                data_end = data_end_match.start()
                raw_value = compiled_raw_flight_data[pos:data_end]
                pos = data_end + 1
            # Otherwise, it means we are reaching the end of the string, so the value
            # will extend to the end of it, and so will its end pos.
            else:
                raw_value = compiled_raw_flight_data[pos:-1]
                pos += len(raw_value)

        if value_class != "T":
            value = orjson.loads(raw_value)
        else:
            value = raw_value
        
        resolved = resolve_type(
            value=value,
            value_class=value_class,
            index=index,
        )
        if index is None:
            if index not in indexed_result:
                indexed_result[index] = []
            indexed_result[index].append(resolved)
        else:
            indexed_result[index] = resolved

    return indexed_result

def get_flight_data(value: _supported_tree):
    """Returns the flight data of the page (the data contained in `self.__next_f`).

    Args:
        value (_supported_tree): The page to get the data from.

    Returns:
        dict[int, Any] | None: The flight data, if it exists, otherwise, None.
    """
    if (raw_flight_data := get_raw_flight_data(value=value)) is not None:
        decoded_raw_flight_data = decode_raw_flight_data(raw_flight_data=raw_flight_data)
        return parse_decoded_raw_flight_data(decoded_raw_flight_data=decoded_raw_flight_data)