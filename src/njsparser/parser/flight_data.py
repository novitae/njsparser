"""Part of the lib to interract with the nextjs data located looking like `self.__next_f.push(1, "...")`"""

from typing import Any, List, Union, TypeVar
import orjson
import re
import base64
import string
from enum import Enum
from pydantic import ValidationError

from ..utils import make_tree, _supported_tree, logger
from .types import resolve_type, Element, Stream, TE

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

FD = dict[int, TE]

# The row tags as React reads them, in `processBinaryChunk` of `ReactFlightClient.js`.
_length_prefixed_tags = frozenset("TbAOoUSsLlGgMmV")
_tags = _length_prefixed_tags | frozenset(string.ascii_uppercase + "#rx")
_stream_tags = frozenset("RrXx")

_re_reference = re.compile(r"\$([0-9a-f]+)")

def _resolve_references(value: Any, rows: FD) -> Any:
    if isinstance(value, list):
        return [_resolve_references(item, rows) for item in value]
    if isinstance(value, str) and (match := _re_reference.fullmatch(value)):
        row = rows.get(int(match.group(1), 16))
        if row is not None and isinstance(row.value, str):
            return row.value
    return value

def _resolve_row(raw_value: bytes, value_class: str | None, index: int | None, rows: FD) -> TE:
    if value_class in _length_prefixed_tags:
        value = raw_value.decode()
    elif not raw_value:
        value = None
    else:
        try:
            value = orjson.loads(raw_value)
        except orjson.JSONDecodeError:
            logger.warning( "Couldn't decode the value of class "
                           f"`{value_class}` at index `{index}`. Giving `Element`." )
            return Element(value=raw_value.decode(), value_class=value_class, index=index)
    if value_class == "I":
        # React moves only strings out of an `"I"` row, and writes them before it.
        value = _resolve_references(value, rows)
    try:
        return resolve_type(value=value, value_class=value_class, index=index)
    except ValidationError as error:
        logger.warning( f"The value of class `{value_class}` at index `{index}` "
                        f"is not a valid `{error.title}`. Giving `Element`." )
        return Element(value=value, value_class=value_class, index=index)

def _iter_rows(data: bytes):
    pos = 0
    while (index_end := data.find(b":", pos)) != -1:
        tag_pos = index_end + 1
        tag = chr(data[tag_pos]) if tag_pos < len(data) else ""
        try:
            index = int(data[pos:index_end], 16) if index_end > pos else None
            if tag in _length_prefixed_tags:
                length_end = data.index(b",", tag_pos)
                start = length_end + 1
                end = pos = start + int(data[tag_pos + 1:length_end], 16)
            else:
                start = tag_pos + 1 if tag in _tags else tag_pos
                end = data.find(b"\n", start)
                if end == -1:
                    end = len(data)
                pos = end + 1
        except ValueError:
            logger.warning(f"Couldn't read the row at byte `{pos}`. Skipping its line.")
            line_end = data.find(b"\n", pos)
            if line_end == -1:
                return
            pos = line_end + 1
            continue
        raw_value = data[start:end]
        value_class = tag if tag in _tags else None
        # A hint row keeps its code in the class, as in `"HL"`.
        if value_class == "H" and raw_value:
            value_class, raw_value = value_class + chr(raw_value[0]), raw_value[1:]
        yield index, value_class, raw_value

def parse_decoded_raw_flight_data(decoded_raw_flight_data: List[str]) -> FD:
    # Here we join, then encode the decoded raw flight data. It is important to encode
    # it, otherwise some values in string will take way more characters, and the text
    # size announced in `"T"` will not be pointing to the correct text end.
    compiled_raw_flight_data = "".join(decoded_raw_flight_data).encode()
    indexed_result, streams = {}, {}
    for index, value_class, raw_value in _iter_rows(compiled_raw_flight_data):
        # The rows of a stream share its index until a `"C"` row closes it. The
        # stream is built once all rows are read, and `None` keeps its place.
        if value_class in _stream_tags:
            streams[index] = (value_class, [])
            indexed_result[index] = None
            continue
        if index in streams and value_class == "C" and not raw_value:
            continue

        # An empty value is `None`. A value that can't be decoded, or isn't valid
        # for its type, is kept as a plain `Element`, so that one row can't stop
        # the rest from being parsed.
        resolved = _resolve_row(
            raw_value=raw_value,
            value_class=value_class,
            index=index,
            rows=indexed_result,
        )
        if index in streams:
            streams[index][1].append(resolved)
        elif index is None:
            if index not in indexed_result:
                indexed_result[index] = []
            indexed_result[index].append(resolved)
        else:
            indexed_result[index] = resolved

    for index, (value_class, chunks) in streams.items():
        indexed_result[index] = Stream(value=chunks, value_class=value_class, index=index)
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