from typing import Any, Literal, Type, TypeVar, TypedDict
from lxml import etree
from pydantic.dataclasses import dataclass
from dataclasses import is_dataclass
from enum import Enum

from ..utils import logger, join
from .urls import _N

ENABLE_TYPE_VERIF = True

__all__ = (
    "Element",
    "HintPreload",
    "Module",
    "Text",
    "Data",
    "EmptyData",
    "SpecialData",
    "HTMLElement",
    "DataContainer",
    "DataParent",
    "URLQuery",
    "is_flight_data_obj",
    "RSCPayloadVersion",
    "RSCPayload",
    "Error",
    "resolve_type",
    "T",
)

TE = TypeVar('TE', bound='Element')

@dataclass(frozen=True)
class Element:
    "An element contained in flight data"
    value: Any
    "The value of the element."
    value_class: str | None
    "The class of the value."
    index: int | None = None
    "The index of the item in the flight data."

@dataclass(frozen=True)
class HintPreload(Element):
    """Represents a `"HL"` object. It is used to place some `<link>` tags into
    the head of the document. Here are some examples of values:

    ```python
    >>> hl1 = HintPreload(
    ...     value=[
    ...         "/_next/static/media/93f479601ee12b01-s.p.woff2",
    ...         "font",
    ...         {"crossOrigin": "", "type": "font/woff2"}
    ...     ],
    ...     value_class="HL",
    ... )
    >>> hl1.href
    '/_next/static/media/93f479601ee12b01-s.p.woff2'
    >>> hl1.type_name
    'font'
    >>> hl1.attrs
    {"crossOrigin": "", "type": "font/woff2"}
    >>> 
    >>> hl2 = HintPreload(
    ...     value=[
    ...         "/_next/static/css/baf446a5c20b5fd4.css?dpl=dpl_F2qLi1zuzNsnuiFMqRXyYU9dbJYw",
    ...         "style"
    ...     ],
    ...     value_class="HL",
    ... )
    >>> hl2.href
    '/_next/static/css/baf446a5c20b5fd4.css?dpl=dpl_F2qLi1zuzNsnuiFMqRXyYU9dbJYw'
    >>> hl2.type_name
    'style'
    >>> hl2.attrs
    >>> 
    ```
    """
    value: list
    value_class = "HL"

    def __post_init__(self):
        if ENABLE_TYPE_VERIF is True:
            assert isinstance(self.value, list)
            assert 2 <= len(self.value) <= 3
            assert isinstance(self.href, str)
            assert isinstance(self.type_name, str)
            assert self.attrs is None or isinstance(self.attrs, dict)

    @property
    def href(self) -> str:
        """The href of the object.

        Returns:
            str: The href the link points to.
        """
        return self.value[0]
    
    @property
    def type_name(self) -> Literal["font", "style"] | str:
        """The type name of the object.

        Returns:
            str: The type name (font, style, ...)
        """
        return self.value[1]
    
    @property
    def attrs(self) -> None | dict[str, str]:
        """The additional attributes of the object.

        Returns:
            None | dict[str, str]: The dict of it, or None if not attrs.
        """
        if len(self.value) >= 3:
            return self.value[2]

    # # TODO
    # def html(self):
    #     element = etree.Element("link", href=self.href)
    #     match self.type_name:
    #         case "font":
    #             element.set("rel", "preload")
    #             element.set("as", "font")
    #             for key, value in self.attrs.items():
    #                 element.set(key, value)
    #         case "style":
    #             element.set("rel", "stylesheet")
    #             element.set("data-precedence", "next")
    #         case _:
    #             raise NotImplementedError( f'type name {self.type_name} is not yet '
    #                                         'supported, please open an issue about it.' )
    #     return etree.tostring(element, method="html").decode("utf-8")

@dataclass(frozen=True)
class Module(Element):
    """Represents a `"I"` object. It is used to import some modules (list of
    scripts). Here is an usage example:

    ```python
    >>> i = Module(
    ...     value=[
    ...         30777,
    ...         [
    ...             "71523",
    ...             "static/chunks/25c8a87d-0d1c991f726a4cc1.js",
    ...             "10411",
    ...             "static/chunks/app/(webapp)/%5Blang%5D/(public)/user/layout-bd7c1d222b477529.js"
    ...         ],
    ...         "default"
    ...     ],
    ...     value_class="I",
    ... )
    >>> i.module_id
    30777
    >>> i.module_chunks_raw()
    {'71523': 'static/chunks/25c8a87d-0d1c991f726a4cc1.js', '10411': 'static/chunks/app/(webapp)/%5Blang%5D/(public)/user/layout-bd7c1d222b477529.js'}
    >>> i.module_chunks
    {'71523': '/_next/static/chunks/25c8a87d-0d1c991f726a4cc1.js', '10411': '/_next/static/chunks/app/(webapp)/%5Blang%5D/(public)/user/layout-bd7c1d222b477529.js'}
    >>> i.module_name
    'default'
    ```
    """
    value: list | dict
    value_class = "I"

    def __post_init__(self):
        if ENABLE_TYPE_VERIF is True:
            assert isinstance(self.value, (list, dict))
            assert 3 <= len(self.value) <= 4
            assert isinstance(self.module_id, int)
            if isinstance(self.value, list):
                assert isinstance(self.value[1], list)
                assert len(self.value[1]) % 2 == 0
            else:
                assert isinstance(self.value["chunks"], list)
            assert isinstance(self.module_name, str)

    @property
    def module_id(self) -> int:
        """Returns the module id.

        Returns:
            int: The module id.
        """
        return self.value[0] if isinstance(self.value, list) else int(self.value["id"])
    
    def module_chunks_raw(self) -> dict[str, str]:
        """Returns the raw script[script id: script relative path].

        Returns:
            dict[str, str]: The script map.
        """
        return dict({
            self.value[1][x]: self.value[1][x+1]
            for x in range(0, len(self.value[1]), 2)
        }) if isinstance(self.value, list) else dict([item.split(":", 1) for item in self.value["chunks"]])
    
    @property
    def module_chunks(self):
        """The modules scripts id to their absolute path.

        Returns:
            dict[str, str]: The script map with absolute paths.
        """
        return {key: join(_N, value) for key, value in self.module_chunks_raw().items()}
    
    @property
    def module_name(self) -> str:
        """The name of the module.

        Returns:
            str: The name of the module.
        """
        return self.value[2] if isinstance(self.value, list) else self.value["name"]
    
    @property
    def is_async(self) -> bool:
        """Tells if the module loading is async or not.

        Returns:
            bool: True if it is.
        """
        if isinstance(self.value, dict):
            return self.value["async"]
        else:
            return False
    
@dataclass(frozen=True)
class Text(Element):
    """Represents a `"T"` flight element. It simply contains text.
    
    ```python
    >>> t = Text(
    ...     value="hello world",
    ...     value_class="T"
    ... )
    >>> t.value
    'hello world'
    >>> t.text
    'hello world'
    ```
    """
    value: str
    value_class = "T"

    def __post_init__(self):
        if ENABLE_TYPE_VERIF is True:
            assert isinstance(self.value, str)

    @property
    def text(self) -> str:
        """Returns the text content.

        Returns:
            str: The text content.
        """
        return self.value
    
@dataclass(frozen=True)
class Data(Element):
    """Represents data in the flight content. It will only be used if the value
    is None. Otherwise it's only here for inherithence of other data objects of
    `value_class` `None`.
    
    ```python
    >>> fd = Data(
    ...     value=["$", "$L1", None, None],
    ...     value_class=None,
    ... )
    >>> fd.content
    >>> print(fd.content)
    None
    >>> fd2 = Data(
    ...     value=["$", "$L1", None, {}],
    ...     value_class=None,
    ... )
    >>> fd2.content
    {}
    ```"""
    value: list
    value_class = None

    def __post_init__(self):
        if ENABLE_TYPE_VERIF is True:
            assert is_flight_data_obj(self.value)
            assert self.content is None or isinstance(self.content, dict)

    @property
    def content(self) -> dict[str, Any] | None:
        return self.value[3]
    
@dataclass(frozen=True)
class EmptyData(Element):
    """Represents flight data that is empty (`None`).
    
    ```python
    >>> ed = Data(
    ...     value=None,
    ...     value_class=None,
    ... )
    >>> ed.value
    >>> print(ed.value)
    None
    """
    value: None
    value_class = None

    def __post_init__(self):
        if ENABLE_TYPE_VERIF is True:
            assert self.value is None

@dataclass(frozen=True)
class SpecialData(Element):
    """Represents any special data in the page. It looks like a string starting
    with a `"$"` character, such as `"$Sreact.suspense"`.
    
    ```python
    >>> fsd = SpecialData(value="$Sreact.suspense", value_class=None)
    >>> fsd.value
    '$Sreact.suspense'
    ```
    """
    value: str
    value_class = None

    def __post_init__(self):
        if ENABLE_TYPE_VERIF is True:
            assert isinstance(self.value, str)
            assert self.value.startswith("$")

@dataclass(frozen=True)
class HTMLElement(Element):
    # https://github.com/facebook/react/blob/1c9b138714a69cd136a3d82769b1fd9a4b318953/packages/react-client/src/ReactFlightClient.js#L1324-L1526
    """Represents a `None` object containing HTML. It is used to store HTML. Here
    is an example:

    ```python
    >>> h = HTMLElement(
    ...     value=[
    ...         "$",
    ...         "link",
    ...         "https://sentry.io",
    ...         {
    ...             "rel": "dns-prefetch",
    ...             "href": "https://sentry.io"
    ...         }
    ...     ],
    ...     value_class=None,
    ... )
    >>> h.tag
    'link'
    >>> h.href
    'https://sentry.io'
    >>> h.attrs
    {'rel': 'dns-prefetch', 'href': 'https://sentry.io'}
    ```
    """
    value: list
    value_class = None

    def __post_init__(self):
        if ENABLE_TYPE_VERIF is True:
            assert is_flight_data_obj(self.value)
            assert isinstance(self.tag, str)
            assert self.href is None or isinstance(self.tag, str)
            assert isinstance(self.attrs, dict)

    @property
    def tag(self) -> str:
        """Returns the tag of the html element, like "div", "link", ...

        Returns:
            str: The tag.
        """
        return self.value[1]
    
    @property
    def href(self) -> str | None:
        """The href, if there is one.

        Returns:
            str | None: The str href or None.
        """
        return self.value[2]
    
    @property
    def attrs(self) -> dict[str, str]:
        """The attributes.

        Returns:
            dict[str, str]: The attributes.
        """
        return self.value[3]
    
@dataclass(frozen=True)
class DataContainer(Element):
    """Represents a list of `Data`. Example:
    ```py
    >>> fdc = DataContainer(
    ...     value=[
    ...         ["$", "div", None, {}],
    ...         ["$", "link", "https://sentry.io", {"rel": "dns-prefetch", "href": "https://sentry.io"}
    ...     ]],
    ...     value_class=None
    ... )
    >>> fdc.value
    [HTMLElement(value=['$', 'div', None, {}], value_class=None, index=None), HTMLElement(value=['$', 'link', 'https://sentry.io', {'rel': 'dns-prefetch', 'href': 'https://sentry.io'}], value_class=None, index=None)]
    >>> item[0]
    HTMLElement(value=['$', 'div', None, {}], value_class=None, index=None)
    >>> item[0].value
    ["$", "div", None, {}]
    >>> item[0].content
    {}
    """
    value: list
    value_class = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "value",
            [
                resolve_type(
                    value=item,
                    value_class=None,
                    index=None,
                ) for item in self.value
            ]
        )
        if ENABLE_TYPE_VERIF is True:
            assert all(is_dataclass(item) for item in self.value)

@dataclass(frozen=True)
class DataParent(Element):
    """Represents an object that has only one key, a `"children"` key.
    
    ```py
    >>> dp = DataParent(
    ...     value=[
    ...         "$",
    ...         "$L16",
    ...         None,
    ...         {
    ...             "children": [
    ...                 "$",
    ...                 "$L17",
    ...                 None,
    ...                 {
    ...                     "profile": {}
    ...                 }
    ...             ]
    ...         }
    ...     ],
    ...     value_class=None,
    ...     index=None
    ... )
    >>> dp.children
    {"profile": {}}
    """
    value: list
    value_class = None

    def __post_init__(self):
        self.value[3].__setitem__(
            "children",
            resolve_type(
                value=self.value[3]["children"],
                value_class=None,
                index=None,
            )
        )
        if ENABLE_TYPE_VERIF is True:
            assert is_flight_data_obj(self.value)
            assert is_dataclass(self.children)

    @property
    def children(self) -> "AnyElement":
        """Returns the children of the parent element.

        Returns:
            Element: The children element.
        """
        return self.value[3]["children"]

@dataclass(frozen=True)
class URLQuery(Element):
    """Represents the values to be set in a url. Example:

    ```python
    >>> phv = URLQuery(
    ...     value=[
    ...         "userId",
    ...         "624dc255c12744f2fdaf90c8",
    ...         "d"
    ...     ],
    ...     value_class=None,
    ... )
    >>> phv.key
    'userId'
    >>> phv.val
    '624dc255c12744f2fdaf90c8'
    ```"""
    value: list
    value_class = None

    def __post_init__(self):
        if ENABLE_TYPE_VERIF is True:
            assert len(self.value) == 3
            assert isinstance(self.key, str)
            assert isinstance(self.val, str)

    @property
    def key(self) -> str:
        """The key of the URLQuery.

        Returns:
            str: The key.
        """
        return self.value[0]
    
    @property
    def val(self) -> str:
        """The value (in the meaning "corresponding to the key") of
        the URLQuery.

        Returns:
            str: The value.
        """
        return self.value[1]

def is_flight_data_obj(value: Any):
    """Tells if the given object is a flight data item.

    Args:
        value (Any): The object.

    Returns:
        bool: True if it is, False if not.
    """
    return isinstance(value, list) \
        and len(value) == 4 \
        and value[0] == "$" \
        and isinstance(value[1], str) \
        and (value[2] is None or isinstance(value[2], str))

class RSCPayloadVersion(int, Enum):
    """The RSCPayloadVersion. I have no idea what are the real names or version
    codes, so i will just name them as old and new, will add more if find."""
    old = 0
    new = 1
    
@dataclass(frozen=True)
class RSCPayload(Element):
    """Represents the RCSPayload, which is the payload containing infos about the
    page. It contains a tree that, read by nextjs and react, will load the whole
    page correctly.

    https://github.com/vercel/next.js/blob/965fe24d91d08567751339756e51f2cf9d0e3188/packages/next/src/server/app-render/types.ts#L224-L243
    """
    value: dict | list
    value_class = None

    def __post_init__(self):
        if ENABLE_TYPE_VERIF is True:
            assert is_flight_data_obj(self.value) or isinstance(self.value, dict)
            assert isinstance(self.build_id, str)

    def _version(self) -> RSCPayloadVersion:
        if isinstance(self.value, list) and len(self.value) == 4:
            return RSCPayloadVersion.old
        elif isinstance(self.value, dict) and "b" in self.value:
            return RSCPayloadVersion.new
        else:
            raise ValueError('unknown flight rcs payload version')

    @property
    def build_id(self) -> str:
        """Gives the build id from the rscpayload.

        Returns:
            str: The build id.
        """
        match self._version():
            case RSCPayloadVersion.new:
                return self.value["b"]
            case RSCPayloadVersion.old:
                return self.value[3]["buildId"]
            
@dataclass(frozen=True)
class Error(Element):
    """Represents a `"E"` (error) flight element. It contains an error.
    
    ```python
    >>> fe = Text(
    ...     value={"digest": "NEXT_NOT_FOUND"},
    ...     value_class="E"
    ... )
    >>> fe.digest
    'NEXT_NOT_FOUND'
    ```"""
    value: dict
    value_class = "E"

    def __post_init__(self):
        if ENABLE_TYPE_VERIF is True:
            assert isinstance(self.value, dict)
            assert "digest" in self.value
            assert isinstance(self.digest, str)

    @property
    def digest(self) -> str:
        """The error code (digest).

        Returns:
            str: The error code.
        """
        return self.value["digest"]

_element_keys = set(["value", "value_class", "index"])
_dumped_element_keys = _element_keys.union({"cls"})
_types: dict[str, Type[Element]] = {
    item.value_class: item for item in [
        HintPreload,
        Module,
        Text,
        Error,
    ]
}
def resolve_type(
    value: Any,
    value_class: str | None,
    index: int,
    cls: Type[Element] = None,
) -> "AnyElement":
    """Find the appropriate dataclass object to init the given value.

    Args:
        value (Any): The value of the flight data item.
        value_class (str | None): The class of the flight data item.
        index (int): The index the flight data.
        cls (Type[Element], optional): The class to use for the element.
            Default on None, will find it by itself.

    Returns:
        Element: The appropriate element.
    """
    if isinstance(value, dict) and _element_keys <= set(value.keys()):
        return resolve_type(**value)
    elif cls is not None and isinstance(cls, str):
        cls = _tl2obj[cls]
    else:
        if value_class is None:
            if isinstance(value, list):
                if is_flight_data_obj(value=value):
                    if value[1].startswith("$"):
                        if value[3] is None:
                            cls = Data
                        elif "buildId" in value[3]:
                            cls = RSCPayload
                        elif len(value[3]) == 1 and "children" in value[3]:
                            cls = DataParent
                        else:
                            cls = Data
                    else:
                        cls = HTMLElement
                elif len(value) == 3 and value[2] == "d" and all(isinstance(item, str) for item in value):
                    cls = URLQuery
                else:
                    cls = DataContainer
            elif value is None:
                cls = EmptyData
            elif isinstance(value, dict) and index == 0:
                cls = RSCPayload
            elif isinstance(value, str) and value.startswith("$"):
                cls = SpecialData
        elif value_class in _types:
            cls = _types[value_class]
    if cls is None:
        if index == 0:
            raise ValueError( 'Data at index 0 did not find any object '
                              'to store its RSCPayload.' )
        logger.warning( "Couldn't find an appropriate type for given "
                       f"class `{value_class}`. Giving `Element`." )
        cls = Element
    return cls(value=value, value_class=value_class, index=index)

class T(dict[str, Type[TE]]):
    Element = Element
    HintPreload = HintPreload
    Module = Module
    Text = Text
    Data = Data
    EmptyData = EmptyData
    SpecialData = SpecialData
    HTMLElement = HTMLElement
    DataContainer = DataContainer
    DataParent = DataParent
    URLQuery = URLQuery
    RSCPayload = RSCPayload
    Error = Error

AnyElement = Element | HintPreload | Module | Text | Data | EmptyData | SpecialData | \
    HTMLElement | DataContainer | DataParent | URLQuery | RSCPayload | Error

_tl2obj = {
    "Element": Element,
    "HintPreload": HintPreload,
    "Module": Module,
    "Text": Text,
    "Data": Data,
    "EmptyData": EmptyData,
    "SpecialData": SpecialData,
    "HTMLElement": HTMLElement,
    "DataContainer": DataContainer,
    "DataParent": DataParent,
    "URLQuery": URLQuery,
    "RSCPayload": RSCPayload,
    "Error": Error,
}
