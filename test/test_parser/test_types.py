from njsparser.parser.types import *
from njsparser.tools import findall_in_flight_data, default
from dataclasses import FrozenInstanceError
from pydantic import ValidationError
import orjson
import pytest

def test_Element():
    with pytest.raises(ValueError):
        Element(value="")
    Element(value="", value_class="", index=1)

def test_Element():
    f = Element(value="hi", value_class=None, index=1)
    with pytest.raises(FrozenInstanceError):
        f.value = "hello"

_flightHintPreloadPayload_1 = dict(
    value=[
        (href1 := "/_next/static/media/569ce4b8f30dc480-s.p.woff2"),
        (type_name1 := "font"),
        (attrs1 := {"crossOrigin": "", "type": "font/woff2"})
    ],
    value_class="HL",
    index=1,
)
_flightHintPreloadPayload_2 = dict(
    value=[
        (href2 := "/_next/static/css/3a4b7cc0153d49b4.css?dpl=dpl_F2qLi1zuzNsnuiFMqRXyYU9dbJYw"),
        (type_name2 := "style")
    ],
    value_class="HL",
    index=1,
)
def test_HintPreload():
    with pytest.raises(ValidationError):
        HintPreload(value=["hello"])
    hl1 = HintPreload(**_flightHintPreloadPayload_1)
    assert hl1.href == href1
    assert hl1.type_name == type_name1
    assert hl1.attrs == attrs1
    hl2 = HintPreload(**_flightHintPreloadPayload_2)
    assert hl2.href == href2
    assert hl2.type_name == type_name2
    assert hl2.attrs is None

def test_serializer_default():
    orjson.dumps(
        Element(value="", value_class="", index=1),
        default=default,
        option=orjson.OPT_PASSTHROUGH_DATACLASS
    )

_flightModulePayload_1 = dict(
    value=[
        30777,
        [
            "71523",
            "static/chunks/25c8a87d-0d1c991f726a4cc1.js",
            "10411",
            "static/chunks/app/(webapp)/%5Blang%5D/(public)/user/layout-bd7c1d222b477529.js"
        ],
        "default"
    ],
    value_class="I",
    index=1,
)
_flightModulePayload_2 = dict(
    value={
        'id': '47858',
        'chunks': [
            '272:static/chunks/webpack-2f0e36f832c3608a.js',
            '667:static/chunks/2443530c-7d590f93d1ab76bc.js',
            '139:static/chunks/139-1e0b88e46566ba7f.js'
        ],
        'name': '',
        'async': False
    },
    value_class="I",
    index=1,
)
def test_Module():
    i = Module(**_flightModulePayload_1)
    assert i.module_id == 30777
    assert i.module_chunks_raw() == {'71523': 'static/chunks/25c8a87d-0d1c991f726a4cc1.js', '10411': 'static/chunks/app/(webapp)/%5Blang%5D/(public)/user/layout-bd7c1d222b477529.js'}
    assert i.module_chunks == {'71523': '/_next/static/chunks/25c8a87d-0d1c991f726a4cc1.js', '10411': '/_next/static/chunks/app/(webapp)/%5Blang%5D/(public)/user/layout-bd7c1d222b477529.js'}
    assert i.module_name == "default"
    assert i.is_async is False
    i2 = Module(**_flightModulePayload_2)
    assert i2.module_id == 47858
    assert i2.module_chunks_raw() == {'272': 'static/chunks/webpack-2f0e36f832c3608a.js', '667': 'static/chunks/2443530c-7d590f93d1ab76bc.js', '139': 'static/chunks/139-1e0b88e46566ba7f.js'}
    assert i2.module_name == ""
    assert i2.is_async is False

_flightTextPayload = dict(value=(hw := "hello world"), value_class="T", index=1)
def test_Text():
    t = Text(**_flightTextPayload)
    assert t.value == t.text == hw

_flightDataPayload_1 = dict(value=["$", "$L1", None, None], value_class=None, index=1)
_flightDataPayload_2 = dict(value=["$", "$L1", None, {}], value_class=None, index=1)
def test_Data():
    assert Data(**_flightDataPayload_1).content is None
    assert Data(**_flightDataPayload_2).content == {}

_flightEmptyDataPayload = dict(value=None, value_class=None, index=1)
def test_EmptyData():
    assert EmptyData(**_flightEmptyDataPayload).value is None

_flightSpecialDataPayload = dict(value="$Sreact.suspense", value_class=None, index=1)
def test_SpecialData():
    assert SpecialData(**_flightSpecialDataPayload).value == "$Sreact.suspense"

_flightHTMLElementPayload_1 = dict(
    value=["$", "div", None, {}],
    value_class=None,
    index=1,
)
_flightHTMLElementPayload_2 = dict(
    value=[
        "$",
        "link",
        "https://sentry.io",
        {"rel": "dns-prefetch", "href": "https://sentry.io"}
    ],
    value_class=None,
    index=1,
)
def test_HTMLElement():
    h1 = HTMLElement(**_flightHTMLElementPayload_1)
    assert h1.tag == 'div'
    assert h1.href is None
    assert h1.attrs == {}
    h2 = HTMLElement(**_flightHTMLElementPayload_2)
    assert h2.tag == 'link'
    assert h2.href == 'https://sentry.io'
    assert h2.attrs == {'rel': 'dns-prefetch', 'href': 'https://sentry.io'}

_flightDataContainerPayload = dict(
    value=[ _flightHTMLElementPayload_1["value"],
            _flightHTMLElementPayload_2["value"]],
    value_class=None,
    index=1,
)
def test_DataContainer():
    dcp = DataContainer(**_flightDataContainerPayload)
    elems = [HTMLElement(item, None, None) for item in _flightDataContainerPayload["value"]]
    assert dcp.value == elems
    fd = {0: dcp}
    assert findall_in_flight_data(fd, [HTMLElement], recursive=False) == []
    assert findall_in_flight_data(fd, [HTMLElement], recursive=True) == dcp.value
    assert findall_in_flight_data(fd, [RSCPayload], recursive=False) == []
    assert findall_in_flight_data(fd, [RSCPayload]) == []

_flightDataParentPayload = dict(
    value=[
        "$",
        "$L16",
        None,
        {
            "children": [
                "$",
                "$L17",
                None,
                {
                    "profile": {}
                }
            ]
        }
    ],
    value_class=None,
    index=None
)
def test_DataParent():
    dp = DataParent(**_flightDataParentPayload)
    assert dp.children.content == {"profile": {}}

_flightURLQuery = dict(
    value=(phv := ["key", "val", "d"]),
    value_class=None,
    index=1,
)
def test_URLQuery():
    urlp = URLQuery(**_flightURLQuery)
    assert urlp.key == phv[0]
    assert urlp.val == phv[1]

_flightRSCPayload_old = dict(
    value=["$", "$L1", None, {"buildId": (iam := "i am a build id")}],
    value_class=None,
    index=0,
)
_flightRSCPayload_new = dict(
    value={"b": (iamn := "i am a new build id")},
    value_class=None,
    index=0,
)
def test_RSCPayload():
    rscp1 = RSCPayload(**_flightRSCPayload_old)
    assert rscp1._version() == RSCPayloadVersion.old
    assert rscp1.build_id == iam
    rscp2 = RSCPayload(**_flightRSCPayload_new)
    assert rscp2._version() == RSCPayloadVersion.new
    assert rscp2.build_id == iamn

_flightErrorPayload = dict(
    value={"digest": (err := "NEXT_NOT_FOUND")},
    value_class="E",
    index=1,
)
def test_Error():
    fe = Error(**_flightErrorPayload)
    assert fe.digest == err

def test_resolve_type():
    assert isinstance(resolve_type(**_flightHintPreloadPayload_1), HintPreload)
    assert isinstance(resolve_type(**_flightHintPreloadPayload_2), HintPreload)
    assert isinstance(resolve_type(**_flightModulePayload_1), Module)
    assert isinstance(resolve_type(**_flightModulePayload_2), Module)
    assert isinstance(resolve_type(**_flightTextPayload), Text)
    assert isinstance(resolve_type(**_flightDataPayload_1), Data)
    assert isinstance(resolve_type(**_flightDataPayload_2), Data)
    assert isinstance(resolve_type(**_flightEmptyDataPayload), EmptyData)
    assert isinstance(resolve_type(**_flightSpecialDataPayload), SpecialData)
    assert isinstance(resolve_type(**_flightURLQuery), URLQuery)
    assert isinstance(resolve_type(**_flightDataContainerPayload), DataContainer)
    assert isinstance(resolve_type(**_flightHTMLElementPayload_1), HTMLElement)
    assert isinstance(resolve_type(**_flightHTMLElementPayload_2), HTMLElement)
    assert isinstance(resolve_type(**_flightRSCPayload_old), RSCPayload)
    assert isinstance(resolve_type(**_flightRSCPayload_new), RSCPayload)
    assert isinstance((error_obj := resolve_type(**_flightErrorPayload)), Error)
    ready_serialized = default(error_obj)
    assert isinstance(resolve_type(**ready_serialized), Error)
    with pytest.raises(KeyError):
        resolve_type(
            value="val",
            value_class=None,
            index=None,
            cls="WONTEXISTSTS",
        )