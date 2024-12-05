from njsparser.parser.types import *
from dataclasses import FrozenInstanceError
import pytest

def test_FlightElement():
    f = FlightElement(value="hi", value_class=None)
    with pytest.raises(FrozenInstanceError):
        f.value = "hello"

_flightHintPreloadPayload_1 = dict(
    value=[
        (href1 := "/_next/static/media/569ce4b8f30dc480-s.p.woff2"),
        (type_name1 := "font"),
        (attrs1 := {"crossOrigin": "", "type": "font/woff2"})
    ],
    value_class="HL",
)
_flightHintPreloadPayload_2 = dict(
    value=[
        (href2 := "/_next/static/css/3a4b7cc0153d49b4.css?dpl=dpl_F2qLi1zuzNsnuiFMqRXyYU9dbJYw"),
        (type_name2 := "style")
    ],
    value_class="HL",
)
def test_HeadLink():
    with pytest.raises(TypeError):
        FlightHintPreload(value=["hello"])
    hl1 = FlightHintPreload(**_flightHintPreloadPayload_1)
    assert hl1.href == href1
    assert hl1.type_name == type_name1
    assert hl1.attrs == attrs1
    hl2 = FlightHintPreload(**_flightHintPreloadPayload_2)
    assert hl2.href == href2
    assert hl2.type_name == type_name2
    assert hl2.attrs is None

_flightModulePayload = dict(
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
)
def test_FlightModule():
    i = FlightModule(**_flightModulePayload)
    assert i.module_id == 30777
    assert i.module_scripts_raw() == {'71523': 'static/chunks/25c8a87d-0d1c991f726a4cc1.js', '10411': 'static/chunks/app/(webapp)/%5Blang%5D/(public)/user/layout-bd7c1d222b477529.js'}
    assert i.module_scripts == {'71523': '/_next/static/chunks/25c8a87d-0d1c991f726a4cc1.js', '10411': '/_next/static/chunks/app/(webapp)/%5Blang%5D/(public)/user/layout-bd7c1d222b477529.js'}
    assert i.module_name == "default"

_flightHTMLElementPayload_1 = dict(
    value=["$", "div", None, {}],
    value_class=None,
)
_flightHTMLElementPayload_2 = dict(
    value=[
        "$",
        "link",
        "https://sentry.io",
        {"rel": "dns-prefetch", "href": "https://sentry.io"}
    ],
    value_class=None,
)
def test_FlightHTMLElement():
    h1 = FlightHTMLElement(**_flightHTMLElementPayload_1)
    assert h1.tag == 'div'
    assert h1.href is None
    assert h1.attrs == {}
    h2 = FlightHTMLElement(**_flightHTMLElementPayload_2)
    assert h2.tag == 'link'
    assert h2.href == 'https://sentry.io'
    assert h2.attrs == {'rel': 'dns-prefetch', 'href': 'https://sentry.io'}

_flightTextPayload = dict(value=(hw := "hello world"), value_class="T")
def test_FlightText():
    t = FlightText(**_flightTextPayload)
    assert t.value == t.text == hw

_flightRSCPayload_old = dict(
    value=["$", "$L1", None, {"buildId": (iam := "i am a build id")}],
    value_class=None,
)
_flightRSCPayload_new = dict(
    value={"b": (iamn := "i am a new build id")},
    value_class=None,
)
def test_FlightRSCPayload():
    rscp1 = FlightRSCPayload(**_flightRSCPayload_old)
    assert rscp1._version() == FlightRSCPayloadVersion.old
    assert rscp1.build_id == iam
    rscp2 = FlightRSCPayload(**_flightRSCPayload_new)
    assert rscp2._version() == FlightRSCPayloadVersion.new
    assert rscp2.build_id == iamn

_flightErrorPayload = dict(
    value={"digest": (err := "NEXT_NOT_FOUND")},
    value_class="E",
)
def test_FlightError():
    fe = FlightError(**_flightErrorPayload)
    assert fe.digest == err

def test_resolve_type():
    assert isinstance(resolve_type(**_flightHintPreloadPayload_1, index=1), FlightHintPreload)
    assert isinstance(resolve_type(**_flightHintPreloadPayload_2, index=1), FlightHintPreload)
    assert isinstance(resolve_type(**_flightModulePayload, index=1), FlightModule)
    assert isinstance(resolve_type(**_flightHTMLElementPayload_1, index=1), FlightHTMLElement)
    assert isinstance(resolve_type(**_flightHTMLElementPayload_2, index=1), FlightHTMLElement)
    assert isinstance(resolve_type(**_flightTextPayload, index=1), FlightText)
    assert isinstance(resolve_type(**_flightRSCPayload_old, index=0), FlightRSCPayload)
    assert isinstance(resolve_type(**_flightRSCPayload_new, index=0), FlightRSCPayload)
    assert isinstance(resolve_type(**_flightErrorPayload, index=1), FlightError)
