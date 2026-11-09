from njsparser.parser.flight_data import (
    has_flight_data,
    get_raw_flight_data,
    get_flight_data,
    parse_decoded_raw_flight_data,
)
from njsparser.parser.types import Element, RSCPayload, Data, Text, Module

from .. import *

def test_has_flight_data():
    assert has_flight_data(value=nextjs_org_html) is True
    assert has_flight_data(value=x_com_html) is False
    assert has_flight_data(value=m_soundcloud_com_html) is False

def test_get_raw_flight_data():
    assert get_raw_flight_data(value=nextjs_org_html) is not None
    assert get_flight_data(value=nextjs_org_html) is not None
    assert get_raw_flight_data(value=x_com_html) is None
    assert get_flight_data(value=x_com_html) is None
    assert get_raw_flight_data(value=m_soundcloud_com_html) is None
    assert get_flight_data(value=m_soundcloud_com_html) is None
    assert get_raw_flight_data(value=mintstars_com_html) is not None
    assert get_flight_data(value=mintstars_com_html) is not None

_decoded_raw_flight_data_with_bad_rows = [
    '0:{"b":"build-id"}\n',
    '1:["$","$L5",null,{"id":"car"}]\n',
    '2:T5,hello',
    'a:X\n',
    'b:I[335250,["$4","$5","$6"],"default"]\n',
    'c:[1,\n',
    'd:C\n',
]

def test_parse_decoded_raw_flight_data_keeps_valid_rows():
    fd = parse_decoded_raw_flight_data(decoded_raw_flight_data=_decoded_raw_flight_data_with_bad_rows)
    assert isinstance(fd[0], RSCPayload)
    assert fd[0].build_id == "build-id"
    assert isinstance(fd[1], Data)
    assert fd[1].content == {"id": "car"}
    assert isinstance(fd[2], Text)
    assert fd[2].text == "hello"

def test_parse_decoded_raw_flight_data_empty_rows():
    fd = parse_decoded_raw_flight_data(decoded_raw_flight_data=_decoded_raw_flight_data_with_bad_rows)
    assert fd[10] == Element(value=None, value_class="X", index=10)
    assert fd[13] == Element(value=None, value_class="C", index=13)

def test_parse_decoded_raw_flight_data_invalid_rows(caplog):
    fd = parse_decoded_raw_flight_data(decoded_raw_flight_data=_decoded_raw_flight_data_with_bad_rows)
    assert fd[11] == Element(value=[335250, ["$4", "$5", "$6"], "default"], value_class="I", index=11)
    assert fd[12] == Element(value="[1,", value_class=None, index=12)
    assert "index `11`" in caplog.text
    assert "index `12`" in caplog.text

_decoded_raw_flight_data_with_module_references = [
    '4:"https://example.com/_next/static/chunks/a.js"\n',
    '5:"https://example.com/_next/static/chunks/b.js"\n',
    '6:"https://example.com/_next/static/chunks/c.js"\n',
    '7:"ClientSegmentRoot"\n',
    '8:I[335250,["$4","$5","$6"],"$7"]\n',
]

def test_parse_decoded_raw_flight_data_module_references():
    fd = parse_decoded_raw_flight_data(decoded_raw_flight_data=_decoded_raw_flight_data_with_module_references)
    assert isinstance(fd[8], Module)
    assert list(fd[8].module_chunks.values()) == [
        "https://example.com/_next/static/chunks/a.js",
        "https://example.com/_next/static/chunks/b.js",
        "https://example.com/_next/static/chunks/c.js",
    ]
    assert fd[8].module_name == "ClientSegmentRoot"
