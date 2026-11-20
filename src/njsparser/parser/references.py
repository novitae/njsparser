"""Part of the lib that follows the references flight data rows make to each other, like `"$1f"`."""

from typing import Any, Generator
import re

from .flight_data import FD
from .types import Element

# As React reads them in `parseModelString` of `ReactFlightClient.js`: `"$1f"` is
# row `1f`, `"$1f:props:listing"` a value inside it, `"$L1f"` a row that is sent
# later and `"$@1f"` the result of a promise.
_re_reference = re.compile(r"\$[L@]?([0-9a-f]+)((?::[^:]*)*)")
# React names the slots of an element, which is written `["$", type, key, props]`.
_element_slots = {"type": 1, "key": 2, "props": 3}
_missing = object()

def _referenced(reference: Any, rows: FD, seen: frozenset = frozenset()) -> Any:
    match = _re_reference.fullmatch(reference) if isinstance(reference, str) else None
    if match is None or reference in seen:
        return _missing
    row = rows.get(int(match.group(1), 16))
    # A row of another class, like an `"I"` module, holds code and not data.
    if not isinstance(row, Element) or row.value_class not in (None, "T"):
        return _missing
    value = row
    for name in match.group(2).split(":")[1:]:
        value = _child(_plain(value, rows, seen | {reference}), name)
    return value

def _child(value: Any, name: str) -> Any:
    try:
        if isinstance(value, dict):
            return value[name]
        if isinstance(value, list):
            if value[:1] == ["$"] and name in _element_slots:
                return value[_element_slots[name]]
            return value[int(name)]
    except (KeyError, IndexError, ValueError):
        pass
    return _missing

def _plain(value: Any, rows: FD, seen: frozenset) -> Any:
    while True:
        if isinstance(value, Element):
            value = value.value
        elif (target := _referenced(value, rows, seen)) is not _missing:
            seen = seen | {value}
            value = target
        else:
            return value

def _resolve(value: Any, rows: FD, active: frozenset, resolved: dict[str, Any]) -> Any:
    while isinstance(value, Element):
        value = value.value
    if isinstance(value, dict):
        return {key: _resolve(item, rows, active, resolved) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve(item, rows, active, resolved) for item in value]
    # A reference to a value that is being resolved is a cycle, and is kept as it is.
    if (target := _referenced(value, rows)) is _missing or value in active:
        return value
    if value not in resolved:
        resolved[value] = _resolve(target, rows, active | {value}, resolved)
    return resolved[value]

def resolve_references(value: Any, rows: FD) -> Any:
    return _resolve(value, rows, frozenset(), {})

def iter_key(value: Any, key: str) -> Generator[Any, None, None]:
    stack = [value]
    while stack:
        value = stack.pop()
        while isinstance(value, Element):
            value = value.value
        if isinstance(value, dict):
            if key in value:
                yield value[key]
            stack.extend(reversed(value.values()))
        elif isinstance(value, list):
            stack.extend(reversed(value))
