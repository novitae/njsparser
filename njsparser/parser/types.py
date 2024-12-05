from typing import Any, Literal, TypedDict
from lxml import etree

# https://github.com/vercel/next.js/blob/965fe24d91d08567751339756e51f2cf9d0e3188/packages/next/src/server/app-render/types.ts#L224-L243
class InitialRSCPayload:
    def __init__(
        self,
        b: str,
        # p: str,
        # c: list[str],
        # i: bool,
        # f: Any, # list[FlightDataPath],
        # m: set[str] | None,
        # G: None, # [React.ComponentType<any>, React.ReactNode | undefined]
        # s: bool,
        # S: bool,
        **kwargs,
    ) -> None:
        self._b = b

    @property
    def build_id(self):
        """The Build ID.

        Returns:
            str: The build id.
        """
        return self._b
    
class FlightObject:
    flight_class_name: Any

    def __init__(self, raw: Any) -> None:
        pass

# class Tag(FlightObject):
#     flight_class_name = None

#     def __init__(self, raw: list[Any]) -> None:
#         assert isinstance(raw, list) and raw[0] == "$"
#         self._raw = raw

#     @property
#     def tag_name(self):
#         return self._raw[1]
    
#     @property
#     def attrs(self) -> dict[str, Any]:
#         return {key: value for key, value in self._raw[3].items() if value != "$undefined"}

class HeadLink(FlightObject):
    """Represents a `"HL"` object. It is used to place some `<link>` tags into
    the head of the document. Here are some examples of values:

    ```python
    >>> hl1 = HeadLink([
    ...     "/_next/static/media/93f479601ee12b01-s.p.woff2",
    ...     "font",
    ...     {"crossOrigin": "", "type": "font/woff2"}
    ... ])
    >>> hl1.href
    '/_next/static/media/93f479601ee12b01-s.p.woff2'
    >>> hl1.type_name
    'font'
    >>> hl1.attrs
    {"crossOrigin": "", "type": "font/woff2"}
    >>> 
    >>> hl2 = HeadLink([
    ...     "/_next/static/css/baf446a5c20b5fd4.css?dpl=dpl_F2qLi1zuzNsnuiFMqRXyYU9dbJYw",
    ...     "style"
    ... ])
    >>> hl2.href
    '/_next/static/css/baf446a5c20b5fd4.css?dpl=dpl_F2qLi1zuzNsnuiFMqRXyYU9dbJYw'
    >>> hl2.type_name
    'style'
    >>> hl2.attrs
    >>> 
    ```
    """
    flight_class_name = "HL"

    def __init__(self, raw: list[Any]) -> None:
        """Init the head link obj.

        Args:
            raw (list[Any]): The raw value of the HL object.
        """
        assert isinstance(raw, list) and len(raw) >= 2
        self._raw = raw

    @property
    def href(self) -> str:
        """The href of the object.

        Returns:
            str: _description_
        """
        return self._raw[0]
    
    @property
    def type_name(self) -> Literal["font", "style"] | str:
        return self._raw[1]
    
    @property
    def attrs(self) -> None | dict[str, str]:
        if len(self._raw) >= 3:
            return self._raw[2]
    
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