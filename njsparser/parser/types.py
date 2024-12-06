from typing import Any, Literal, Type
from lxml import etree
from pydantic.dataclasses import dataclass
from dataclasses import asdict
from enum import Enum

from ..utils import logger, join
from .urls import _N

# TODO: Asserts in the __post_init__ to make sure the data fed isn't bullshit

__all__ = (
    "FlightElement",
    "serializer_default",
    "FlightHintPreload",
    "FlightModule",
    "FlightText",
    "FlightData",
    "FlightEmptyData",
    "FlightSpecialData",
    "FlightHTMLElement",
    "FlightDataContainer",
    "FlightURLQuery",
    "is_flight_data_obj",
    "FlightRSCPayloadVersion",
    "FlightRSCPayload",
    "FlightError",
    "resolve_type",
)

@dataclass(frozen=True)
class FlightElement:
    "An element contained in flight data"
    value: Any
    "The value of the element."
    value_class: str | None
    "The class of the value."
    index: int
    "The index of the item in the flight data."

def serializer_default(obj: Any):
    if isinstance(obj, FlightElement):
        return {**asdict(obj=obj), "cls": type(obj).__name__}
    else:
        raise TypeError(type(obj))

class FlightHintPreload(FlightElement):
    """Represents a `"HL"` object. It is used to place some `<link>` tags into
    the head of the document. Here are some examples of values:

    ```python
    >>> hl1 = FlightHintPreload(
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
    >>> hl2 = FlightHintPreload(
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

class FlightModule(FlightElement):
    """Represents a `"I"` object. It is used to import some modules (list of
    scripts). Here is an usage example:

    ```python
    >>> i = FlightModule(
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
    >>> i.module_scripts_raw()
    {'71523': 'static/chunks/25c8a87d-0d1c991f726a4cc1.js', '10411': 'static/chunks/app/(webapp)/%5Blang%5D/(public)/user/layout-bd7c1d222b477529.js'}
    >>> i.module_scripts
    {'71523': '/_next/static/chunks/25c8a87d-0d1c991f726a4cc1.js', '10411': '/_next/static/chunks/app/(webapp)/%5Blang%5D/(public)/user/layout-bd7c1d222b477529.js'}
    >>> i.module_name
    'default'
    ```
    """
    value: list
    value_class = "I"

    @property
    def module_id(self) -> int:
        """Returns the module id.

        Returns:
            int: The module id.
        """
        return self.value[0]
    
    def module_scripts_raw(self) -> dict[str, str]:
        """Returns the raw script[script id: script relative path].

        Returns:
            dict[str, str]: The script map.
        """
        return dict({
            self.value[1][x]: self.value[1][x+1]
            for x in range(0, len(self.value), 2)
        })
    
    @property
    def module_scripts(self):
        """The modules scripts id to their absolute path.

        Returns:
            dict[str, str]: The script map with absolute paths.
        """
        return {key: join(_N, value) for key, value in self.module_scripts_raw().items()}
    
    @property
    def module_name(self) -> str:
        """The name of the module.

        Returns:
            str: The name of the module.
        """
        return self.value[2]
    
class FlightText(FlightElement):
    """Represents a `"T"` flight element. It simply contains text.
    
    ```python
    >>> t = FlightText(
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

    @property
    def text(self) -> str:
        """Returns the text content.

        Returns:
            str: The text content.
        """
        return self.value
    
class FlightData(FlightElement):
    """Represents data in the flight content. It will only be used if the value
    is None. Otherwise it's only here for inherithence of other data objects of
    `value_class` `None`.
    
    ```python
    >>> fd = FlightData(
    ...     value=None,
    ...     value_class=None,
    ... )
    >>> fd.value
    >>> print(fd.value)
    None
    ```"""
    value: list | None
    value_class = None

    @property
    def content(self) -> dict[str, Any]:
        return self.value[3]
    
class FlightEmptyData(FlightElement):
    """Represents flight data that is empty (`None`)."""
    value: None
    value_class = None

class FlightSpecialData(FlightElement):
    """Represents any special data in the page. It looks like a string starting
    with a `"$"` character, such as `"$Sreact.suspense"`.
    
    ```python
    >>> fsd = FlightSpecialData(value="$Sreact.suspense", value_class=None)
    >>> fsd.value
    '$Sreact.suspense'
    ```
    """
    value: str
    value_class = None

class FlightHTMLElement(FlightElement):
    # https://github.com/facebook/react/blob/1c9b138714a69cd136a3d82769b1fd9a4b318953/packages/react-client/src/ReactFlightClient.js#L1324-L1526
    """Represents a `None` object containing HTML. It is used to store HTML. Here
    is an example:

    ```python
    >>> h = FlightHTMLElement(
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
    
class FlightDataContainer(FlightElement):
    """Represents a list of `FlightData`. As seen on the example lower, you
    will have to instanciate them yourself if you want to treat each one of
    them as a FlightData object (see how `item` is done).

    ```py
    >>> fdc = FlightDataContainer(
    ...     value=[
    ...         ["$", "div", None, {}],
    ...         ["$", "link", "https://sentry.io", {"rel": "dns-prefetch", "href": "https://sentry.io"}
    ...     ]],
    ...     value_class=None
    ... )
    >>> fdc.value
    [["$", "div", None, {}], ["$", "link", "https://sentry.io", {"rel": "dns-prefetch", "href": "https://sentry.io"}]]
    >>> item = FlightData(value=fdc.value[0], value_class=fdc.value_class)
    >>> item.value
    ["$", "div", None, {}]
    >>> item.content
    {}
    """
    value: list
    value_class = None

class FlightURLQuery(FlightElement):
    """Represents the values to be set in a url. Example:

    ```python
    >>> phv = FlightURLQuery(
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

    @property
    def key(self) -> str:
        return self.value[0]
    
    @property
    def val(self) -> str:
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

class FlightRSCPayloadVersion(int, Enum):
    """The RSCPayloadVersion. I have no idea what are the real names or version
    codes, so i will just name them as old and new, will add more if find."""
    old = 0
    new = 1
    
class FlightRSCPayload(FlightElement):
    """Represents the RCSPayload, which is the payload containing infos about the
    page. It contains a tree that, read by nextjs and react, will load the whole
    page correctly.

    https://github.com/vercel/next.js/blob/965fe24d91d08567751339756e51f2cf9d0e3188/packages/next/src/server/app-render/types.ts#L224-L243
    """
    value: dict | list
    value_class = None

    def _version(self) -> FlightRSCPayloadVersion:
        if isinstance(self.value, list) and len(self.value) == 4:
            return FlightRSCPayloadVersion.old
        elif isinstance(self.value, dict) and "b" in self.value:
            return FlightRSCPayloadVersion.new
        else:
            raise ValueError('unknown flight rcs payload version')

    @property
    def build_id(self) -> str:
        """Gives the build id from the rscpayload.

        Returns:
            str: The build id.
        """
        match self._version():
            case FlightRSCPayloadVersion.new:
                return self.value["b"]
            case FlightRSCPayloadVersion.old:
                return self.value[3]["buildId"]
            
class FlightError(FlightElement):
    """Represents a `"E"` (error) flight element. It contains an error.
    
    ```python
    >>> fe = FlightText(
    ...     value={"digest": "NEXT_NOT_FOUND"},
    ...     value_class="E"
    ... )
    >>> fe.digest
    'NEXT_NOT_FOUND'
    ```"""
    value: dict
    value_class = "E"

    @property
    def digest(self) -> str:
        """The error code (digest).

        Returns:
            str: The error code.
        """
        return self.value["digest"]

_types: dict[str, Type[FlightElement]] = {
    item.value_class: item for item in [
        FlightHintPreload,
        FlightModule,
        FlightText,
        FlightError,
    ]
}
def resolve_type(
    value: Any,
    value_class: str | None,
    index: int,
):
    """Find the appropriate dataclass object to init the given value.

    Args:
        value (Any): The value of the flight data item.
        value_class (str | None): The class of the flight data item.
        index (int): The index the flight data.

    Returns:
        FlightElement: The appropriate element.
    """
    cls = None
    if value_class is None:
        if isinstance(value, list):
            if is_flight_data_obj(value=value):
                if value[1].startswith("$"):
                    if value[3] is not None and "buildId" in value[3]:
                        cls = FlightRSCPayload
                    else:
                        cls = FlightData
                else:
                    cls = FlightHTMLElement
            elif value and all([is_flight_data_obj(value=item) for item in value]):
                cls = FlightDataContainer
            elif len(value) == 3 and value[2] == "d" and all(isinstance(item, str) for item in value):
                cls = FlightURLQuery
        elif value is None:
            cls = FlightEmptyData
        elif isinstance(value, dict) and index == 0:
            cls = FlightRSCPayload
        elif isinstance(value, str) and value.startswith("$"):
            cls = FlightSpecialData
    elif value_class in _types:
        cls = _types[value_class]
    if cls is None:
        if index == 0:
            raise ValueError( 'Data at index 0 did not find any object '
                              'to store its RSCPayload.' )
        logger.warning( "Couldn't find an appropriate type for given "
                       f"class `{value_class}`. Giving `FlightElement`." )
        cls = FlightElement
    return cls(value=value, value_class=value_class, index=index)
