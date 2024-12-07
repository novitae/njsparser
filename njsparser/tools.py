from typing import Type, TypeVar, List, Iterable, Callable, Generator, overload

from .utils import _supported_tree, make_tree, logger
from .parser.next_data import has_next_data, get_next_data
from .parser.flight_data import has_flight_data, get_flight_data, FD
from .parser.types import RSCPayload, Element, DataContainer
from .parser.urls import get_next_static_urls, get_base_path, _NS
from .parser.manifests import _manifest_paths

__all__ = (
    "has_nextjs",
    "find_build_id",
    "finditer_in_flight_data",
    "findall_in_flight_data",
    "find_in_flight_data",
)

def has_nextjs(value: _supported_tree):
    """Tells if the page has some nextjs data in it.

    Args:
        value (_supported_tree): The page to check for.

    Returns:
        bool: True if it contains any nextjs data, otherwise, False.
    """
    return any([has_next_data(value=value), has_flight_data(value=value)])

T = TypeVar('T', bound='Element')
C = Callable[[Element], bool]

@overload
def finditer_in_flight_data(
    flight_data: FD | None,
    class_filters: Iterable[Type[T]] = None,
    callback: C = None,
    recursive: bool | None = None,
) -> Generator[T, None, None]:
    """
    An iterator yielding flight data elements of specified types and matching a callback.

    Args:
        flight_data (dict[int, Element]): The flight data. Typically obtained using
            `njsparser.get_flight_data(...)`.
        class_filters (List[Type[T]], optional): A list of classes to filter the flight
            elements by type. If None, no type filtering is applied. Defaults to None.
        callback (Callable[[Element], bool], optional): A function used to further filter
            elements. The function receives a single flight element as an argument and must
            return `True` to include the element in the results, or `False` to exclude it.
            For example, `lambda item: item.index >= 5` includes only elements with an `index`
            attribute greater than or equal to 5. If None, all elements are included. Defaults to None.
        recursive (bool, optional): Will we search recursively for the object ? Defaults
            to True.

    Yields:
        T: Flight elements matching the specified type and callback criteria.
    """
    ...

@overload
def finditer_in_flight_data(
    flight_data: FD | None,
    class_filters: None = None,
    callback: C = None,
    recursive: bool | None = None,
) -> Generator[Element, None, None]:
    """See the main overload for `finditer_in_flight_data`."""
    ...

def finditer_in_flight_data(
    flight_data: FD | None,
    class_filters: list = None,
    callback: C = None,
    recursive: bool | None = None,
):
    if flight_data is None:
        return
    for value in flight_data.values():
        if recursive is not False and type(value) is DataContainer:
            yield from finditer_in_flight_data(
                flight_data=dict(enumerate(value.value)),
                class_filters=class_filters,
                callback=callback,
                recursive=recursive,
            )
        else:
            if (type(value) in class_filters if class_filters is not None else True) \
                    and (True if callback is None else callback(value)):
                yield value

@overload
def findall_in_flight_data(
    flight_data: FD,
    class_filters: Iterable[Type[T]] = None,
    callback: C = None,
    recursive: bool | None = None,
) -> List[T]:
    """
    A function returning all flight data elements of specified types and matching a callback.

    Args:
        flight_data (dict[int, Element]): The flight data, typically obtained using
            `njsparser.get_flight_data(...)`.
        class_filters (List[Type[T]], optional): A list of classes to filter the flight
            elements by type. If None, no type filtering is applied. Defaults to None.
        callback (Callable[[Element], bool], optional): A function used to further filter
            elements. The function receives a single flight element as an argument and must
            return `True` to include the element in the results, or `False` to exclude it.
            For example, `lambda item: item.index >= 5` includes only elements with an `index`
            attribute greater than or equal to 5. If None, all elements are included. Defaults to None.
        recursive (bool, optional): Will we search recursively for the object ? Defaults
            to True.

    Returns:
        List[T]: A list of flight elements matching the specified type and callback criteria.
    """
    ...

# TODO findall_in_flight_elements (list instead of dict)

@overload
def findall_in_flight_data(
    flight_data: FD,
    class_filters: None = None,
    callback: C = None,
    recursive: bool | None = None,
) -> List[Element]:
    """See the main overload for `findall_in_flight_data`."""
    ...

def findall_in_flight_data(
    flight_data: FD,
    class_filters: Iterable[Type[T]] = None,
    callback: C = None,
    recursive: bool | None = None,
):
    return list(
        finditer_in_flight_data(
            flight_data=flight_data,
            class_filters=class_filters,
            callback=callback,
            recursive=recursive,
        )
    )

@overload
def find_in_flight_data(
    flight_data: FD,
    class_filters: Iterable[Type[T]] = None,
    callback: C = None,
    recursive: bool | None = None,
) -> T | None:
    """
    Returns the first flight data element of specified types and matching a callback.

    Args:
        flight_data (dict[int, Element]): The flight data, typically obtained using
            `njsparser.get_flight_data(...)`.
        class_filters (List[Type[T]], optional): A list of classes to filter the flight
            elements by type. If None, no type filtering is applied. Defaults to None.
        callback (Callable[[Element], bool], optional): A function used to further filter
            elements. The function receives a single flight element as an argument and must
            return `True` to include the element in the results, or `False` to exclude it.
            For example, `lambda item: item.index >= 5` includes only elements with an `index`
            attribute greater than or equal to 5. If None, all elements are included. Defaults to None.
        recursive (bool, optional): Will we search recursively for the object ? Defaults
            to True.

    Returns:
        T | None: The first flight element matching the specified type and callback criteria,
        or None if no match is found.
    """
    ...

@overload
def find_in_flight_data(
    flight_data: FD,
    class_filters: None = None,
    callback: C = None,
    recursive: bool | None = None,
) -> Element | None:
    """See the main overload for `find_in_flight_data`."""
    ...

def find_in_flight_data(
    flight_data: FD,
    class_filters: Iterable[Type[T]] = None,
    callback: C = None,
    recursive: bool | None = None,
):
    for item in finditer_in_flight_data(
        flight_data=flight_data,
        class_filters=class_filters,
        callback=callback,
        recursive=recursive,
    ):
        return item
        
def find_build_id(value: _supported_tree) -> str | None:
    """Searches and return (or not) the build id of the given page.

    Args:
        value (_supported_tree): The page to find the build id from.

    Returns:
        str | None: Either the buildId if it was found, or None if it didn't.
    """
    tree = make_tree(value=value)

    # Searches through the static next urls, and if we find anything that ends
    # with `"/_buildManifest.js"` or `"/_ssgManifest.js"`, we can extract the
    # build id from it.
    if (next_static_urls := get_next_static_urls(value=tree)) is not None:
        base_path = get_base_path(value=next_static_urls, remove_domain=False)
        for next_static_url in next_static_urls:
            sliced_su = next_static_url.removeprefix(base_path).removeprefix(_NS)
            for manifest_path in _manifest_paths:
                if sliced_su.endswith(manifest_path):
                    return sliced_su.removesuffix(manifest_path)
                
    # We search for the buildId directly into the `__NEXT_DATA__` script.
    if (next_data := get_next_data(value=tree)) is not None:
        if "buildId" in next_data:
            return next_data["buildId"]
        else:
            logger.warning( "Found a next_data dict in the page, " \
                            "but did't contain any `buildId` key." )
            
    # We search for the builId in the flight data.
    elif (flight_data := get_flight_data(value=tree)) is not None:
        if (found := find_in_flight_data(flight_data, [RSCPayload])) is not None:
            return found.build_id
        else:
            logger.warning( "Found flight data in the page, but " \
                            "couldnt find the build id. If are certain" \
                            " there is one, open an issue with your " \
                            "html to investigate :)" )
