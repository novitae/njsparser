from typing import Type, List, Iterable, Callable, Generator, overload, Self, Any
from dataclasses import is_dataclass, asdict

from .utils import _supported_tree, make_tree, logger
from .parser.next_data import has_next_data, get_next_data
from .parser.flight_data import has_flight_data, get_flight_data, FD, TE
from .parser.types import RSCPayload, Element, DataContainer, T, _tl2obj, resolve_type, DataParent, _dumped_element_keys
from .parser.urls import get_next_static_urls, get_base_path, _NS
from .parser.manifests import _manifest_paths

__all__ = (
    "has_nextjs",
    "find_build_id",
    "finditer_in_flight_data",
    "findall_in_flight_data",
    "find_in_flight_data",
    "BeautifulFD",
    "default",
)

def has_nextjs(value: _supported_tree):
    """Tells if the page has some nextjs data in it.

    Args:
        value (_supported_tree): The page to check for.

    Returns:
        bool: True if it contains any nextjs data, otherwise, False.
    """
    return any([has_next_data(value=value), has_flight_data(value=value)])

C = Callable[[Element], bool]

@overload
def finditer_in_flight_data(
    flight_data: FD | None,
    class_filters: Iterable[Type[TE]] = None,
    callback: C = None,
    recursive: bool | None = None,
) -> Generator[TE, None, None]:
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
    if class_filters is not None and isinstance(class_filters, set) is False:
        class_filters = set(class_filters)
    for value in flight_data.values():
        if recursive is not False and type(value) is DataContainer:
            yield from finditer_in_flight_data(
                flight_data=dict(enumerate(value.value)),
                class_filters=class_filters,
                callback=callback,
                recursive=recursive,
            )
        elif recursive is not False and type(value) is DataParent:
            yield from finditer_in_flight_data(
                flight_data={0: value.children},
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
    flight_data: FD | None,
    class_filters: Iterable[Type[TE]] = None,
    callback: C = None,
    recursive: bool | None = None,
) -> List[TE]:
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
    flight_data: FD | None,
    class_filters: None = None,
    callback: C = None,
    recursive: bool | None = None,
) -> List[Element]:
    """See the main overload for `findall_in_flight_data`."""
    ...

def findall_in_flight_data(
    flight_data: FD | None,
    class_filters: Iterable[Type[TE]] = None,
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
    flight_data: FD | None,
    class_filters: Iterable[Type[TE]] = None,
    callback: C = None,
    recursive: bool | None = None,
) -> TE | None:
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
    flight_data: FD | None,
    class_filters: None = None,
    callback: C = None,
    recursive: bool | None = None,
) -> Element | None:
    """See the main overload for `find_in_flight_data`."""
    ...

def find_in_flight_data(
    flight_data: FD | None,
    class_filters: Iterable[Type[TE]] = None,
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

class BeautifulFD:
    """An object to simply the use and search through flight data.
    
    ```py
    >>> response = requests.get(...)
    >>> fd = BeautifulFD(response.text)
    >>> fd.find()
    """
    def __init__(self, value: FD | _supported_tree):
        """Creates the BeautifulFD object.

        Args:
            value (FD | _supported_tree): The string/bytes HTML, or lxml _Element
                object, or the already made flight data (using the method at
                `njsparser.get_flight_data`). 

        Raises:
            TypeError: The given `value` type is not supported.
        """
        if isinstance(value, dict):
            flight_data = {}
            for key, value in value.items():
                if isinstance(key, str) and key.isdigit():
                    key = int(key)
                elif isinstance(key, int) is False:
                    raise TypeError(f'Given key {key} in flight data dict is neither '
                                     'a digit string, neither an int.' )
                if isinstance(value, dict) and set(value.keys()) == _dumped_element_keys:
                    value = resolve_type(**value)
                elif is_dataclass(value) is False:
                    raise TypeError(f'Given key {key} in flight data dict is neither '
                                     'a digit string, neither an int.' )
                flight_data[key] = value
        elif isinstance(value, _supported_tree):
            flight_data = get_flight_data(value=value)
        else:
            raise TypeError(f'Given type "{type(value)}" is unsupported')
        self._flight_data = flight_data

    def __repr__(self):
        if self is None:
            return f"BeautifulFD(None)"
        else:
            return f"BeautifulFD(<{len(self)} elements>)"
        
    def __len__(self):
        return len(self._flight_data) if self else 0
    
    def __bool__(self):
        return self._flight_data is not None
    
    def __iter__(self):
        if self:
            yield from self._flight_data.items()

    def as_list(self) -> list[Element]:
        """Returns the flight data as a list instead of a dict.

        Returns:
            list[Element]: The list of elements in the flight data.
        """
        return list(self._flight_data.values()) if self else []
    
    @classmethod
    def from_list(cls, l: list[Element | dict], *, via_enumerate: bool = None) -> Self:
        """Will load a from a list of flight data elements, or list of dict
        representing them. If you dumped the `BeautifulFD` with the `.as_list()`
        method, this is what you want to load it back in.

        Args:
            l (list[Element | dict]): The list of lfight data Elements or dicts.
            via_enumerate (bool, optional): If objects do not contain their own
                indexes, it will use their position in the given list as index
                if set to `True`. Defaults to `False`.

        Raises:
            ValueError: Objects do not contain their own indexes, and `via_enumerate`
                is `False`.

        Returns:
            Self: The BeautifulFD object.
        """
        if all(isinstance(item, dict) and "cls" in item for item in l):
            l = [resolve_type(value=item, value_class=None, index=None) for item in l]
        if all(isinstance(item.index, int) for item in l):
            value = {item.index: item for item in l}
        elif via_enumerate is not True:
            raise ValueError( 'Cannot load the given list since elements do not '
                              'all have an index written on them. You can set '
                              '`via_enumerate` to `True` to put the elements '
                              'indexes in the given list as their indexes. ' )
        else:
            value = dict(enumerate(l))
        return cls(value=value)

    @overload
    def find_iter(
        self,
        class_filters: Iterable[Type[TE] | T] = None,
        callback: C = None,
        recursive: bool | None = None,
    ) -> Generator[TE, None, None]:
        """Yields flight data elements of specified types and matching a callback.

        Args:
            flight_data (dict[int, Element]): The flight data. Typically obtained using
                `njsparser.get_flight_data(...)`.
            class_filters (List[Type[T] | T], optional): A list of classes to filter the flight
                elements by type. Can also be the names of the classes. If None, no type
                filtering is applied. Defaults to None.
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
    def find_iter(
        self,
        class_filters: None = None,
        callback: C = None,
        recursive: bool | None = None,
    ) -> Generator[Element, None, None]:
        """See the main overload for `BeautifulFD.find_iter`."""
        ...

    def find_iter(self, class_filters = None, callback: C = None, recursive = None):
        if class_filters is None:
            new_class_filters = None
        else:
            new_class_filters = set()
            for cls in class_filters:
                if is_dataclass(cls):
                    new_class_filters.add(cls)
                else:
                    if cls in _tl2obj:
                        new_class_filters.add(_tl2obj[cls])
                    else:
                        raise KeyError( f'The class filter "{cls}" is not present in the list '
                                        f'of conversion: {list(_tl2obj.keys())}.' )
        yield from finditer_in_flight_data(
            flight_data=self._flight_data,
            class_filters=new_class_filters,
            callback=callback,
            recursive=recursive,
        )

    @overload
    def find_all(
        self,
        class_filters: Iterable[Type[TE] | T] = None,
        callback: C = None,
        recursive: bool | None = None,
    ) -> List[TE]:
        """Returns all elements of specified types and matching a callback.

        Args:
            class_filters (List[Type[T] | T], optional): A list of classes to filter the flight
                elements by type. Can also be the names of the classes. If None, no type
                filtering is applied. Defaults to None.
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

    @overload
    def find_all(
        self,
        class_filters: None = None,
        callback: C = None,
        recursive: bool | None = None,
    ) -> List[Element]:
        """See the main overload for `BeautifulFD.find_all`."""
        ...

    def find_all(self, class_filters = None, callback = None, recursive = None):
        return list(
            self.find_iter(
                class_filters=class_filters,
                callback=callback,
                recursive=recursive,
            )
        )

    @overload
    def find(
        self,
        class_filters: Iterable[Type[TE] | T] = None,
        callback: C = None,
        recursive: bool | None = None,
    ) -> TE | None:
        """Returns the first element of specified types and matching a callback.

        Args:
            class_filters (List[Type[T] | T], optional): A list of classes to filter the flight
                elements by type. Can also be the names of the classes. If None, no type
                filtering is applied. Defaults to None.
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
    def find(
        self,
        class_filters: None = None,
        callback: C = None,
        recursive: bool | None = None,
    ) -> Element | None:
        """See the main overload for `BeautifulFD.find`."""
        ...

    def find(self, class_filters = None, callback = None, recursive = None):
        for item in self.find_iter(
            class_filters=class_filters,
            callback=callback,
            recursive=recursive,
        ):
            return item

def default(obj: Any):
    """The `default` function for json dumpers.

    Args:
        obj (Any): The object to resolve the type of.

    Raises:
        TypeError: The type is not found here.

    Returns:
        dict[str, Any]: _description_
    """
    if isinstance(obj, BeautifulFD):
        return {str(key): value for key, value in obj}
    if isinstance(obj, Element):
        return {**asdict(obj=obj), "cls": type(obj).__name__}
    else:
        raise TypeError(type(obj))
