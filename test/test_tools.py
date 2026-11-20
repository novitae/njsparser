from njsparser.tools import (
    has_nextjs,
    findall_in_flight_data,
    find_in_flight_data,
    find_build_id,
    BeautifulFD,
    resolve_type,
)
from njsparser.parser.flight_data import parse_decoded_raw_flight_data
from njsparser.parser.types import *
from dataclasses import is_dataclass

import pytest

from . import *

def test_has_nextjs():
    assert has_nextjs(value=m_soundcloud_com_html) is True
    assert has_nextjs(value=nextjs_org_html) is True
    assert has_nextjs(value=x_com_html) is False

# `finditer_in_flight_data` ignored since findall_in_flight_data is literally
# a list transformer of it.

flight_data = {
    0: RSCPayload(value={"b": "BUILDID"}, value_class=None, index=0),
    1: Error(value={"digest": "NEXT_NOT_FOUND"}, value_class=None, index=1),
    2: SpecialData(value="$Sreactblahblah", value_class=None, index=2),
    3: Text(value="hello world", value_class=None, index=3),
}
def test_findall_in_flight_data():
    class_filters = (RSCPayload, Module)
    for item in findall_in_flight_data(flight_data, class_filters=class_filters):
        assert isinstance(item, class_filters)
    assert findall_in_flight_data(flight_data) == list(flight_data.values())
    for item in findall_in_flight_data(flight_data, callback=lambda item: bool(item.index % 2)):
        assert item.index % 2 == 1
    assert findall_in_flight_data(None) == []

_recursive_data = {"value": [{"value": None,"value_class": None,"index": None},{"value": False,"value_class": None,"index": None},{"value": ["$","$L16",None,{"children": ["$","$L17",None,{"profile": {}}]}],"value_class": None,"index": None}],"value_class": None,"index": 5,"cls": "DataContainer"}
def test_find_in_flight_data():
    assert find_in_flight_data(flight_data, [URLQuery]) is None
    assert find_in_flight_data(flight_data, [RSCPayload]) == flight_data[0]
    assert find_in_flight_data(None) is None
    assert find_in_flight_data({0: resolve_type(**_recursive_data)}, [Data]).content == {"profile": {}}
    assert find_in_flight_data({0: resolve_type(**_recursive_data)}, [Data], recursive=False) is None

def test_find_build_id():
    assert find_build_id(value=m_soundcloud_com_html) == "1733156665"
    assert find_build_id(value=nextjs_org_html) == "4mSOwJptzzPemGzzI8AOo"
    assert find_build_id(value=x_com_html) is None
    assert find_build_id(value=swag_live_html) == "giz3a1H7OUzfxgxRHIdMx"
    
    # Recursive search here
    assert find_build_id(value=club_fans_html) == "n2xbxZXkzoS6U5w7CgB-T"

def test_BeautifulFD():
    with pytest.raises(TypeError):
        BeautifulFD(None)
    fd = BeautifulFD(club_fans_html)
    assert fd.find() is not None
    assert isinstance(fd.find([Data]), Data)
    assert isinstance(fd.find(["Data"]), Data)
    with pytest.raises(KeyError):
        fd.find(["Datsdfdsfa"])
    for key, value in fd:
        assert isinstance(key, int) and is_dataclass(value)
        break
    assert bool(BeautifulFD({})) is True
    assert len(BeautifulFD({1: URLQuery(value=["x", "y", "d"], value_class=None, index=1)})) == 1
    empty_bfd = BeautifulFD("<html></html>")
    assert bool(empty_bfd) is False
    assert len(BeautifulFD("<html></html>")) == 0
    assert isinstance(empty_bfd.as_list(), list)

_car_fd = BeautifulFD(parse_decoded_raw_flight_data(decoded_raw_flight_data=[
    '1:I[30777,["71523","static/chunks/a.js"],"default"]\n',
    '2:T5,hello',
    '3:["$","div",null,{"children":["$","$L1",null,{"listing":{"make":"MAZDA","description":"$2","seller":{"id":7}},"seller":{"id":7,"name":"Garage"}}]}]\n',
    '4:["$","$L1",null,{"seller":"$3:props:children:props:seller","similar":"$L5"}]\n',
    '5:{"listing":{"make":"FIAT"}}\n',
]))

def test_BeautifulFD_resolve():
    assert _car_fd.resolve("$5") == {"listing": {"make": "FIAT"}}
    assert _car_fd.resolve({"description": "$2", "module": "$L1"}) == {"description": "hello", "module": "$L1"}
    assert BeautifulFD(x_com_html).resolve("$5") == "$5"

def test_BeautifulFD_find_key():
    assert _car_fd.find_key("listing") == {"make": "MAZDA", "description": "hello", "seller": {"id": 7}}
    assert _car_fd.find_key("description") == "hello"
    assert _car_fd.find_key("nope") is None
    assert BeautifulFD(x_com_html).find_key("listing") is None

def test_BeautifulFD_find_key_all():
    assert _car_fd.find_key_all("seller") == [
        {"id": 7, "name": "Garage"},
        {"id": 7},
        {"id": 7, "name": "Garage"},
    ]
    assert _car_fd.find_key_all("similar") == [{"listing": {"make": "FIAT"}}]
    assert _car_fd.find_key_all("nope") == []
    assert BeautifulFD(x_com_html).find_key_all("listing") == []

def test_BeautifulFD_find_key_callback():
    assert _car_fd.find_key("listing", callback=lambda value: value["make"] == "FIAT") == {"make": "FIAT"}
    assert _car_fd.find_key_all("seller", callback=lambda value: "name" not in value) == [{"id": 7}]

def test_BeautifulFD_find_key_within():
    similar = _car_fd.find_key("similar")
    assert _car_fd.find_key("make", within=similar) == "FIAT"
    assert _car_fd.find_key_all("listing", within=_car_fd._flight_data[4]) == [{"make": "FIAT"}]
    assert _car_fd.find_key("description", within=similar) is None

def test_BeautifulFD_find_key_in_pages():
    swag_live = BeautifulFD(swag_live_html)
    assert all(not html.startswith("$") for html in swag_live.find_key_iter("__html"))
    assert swag_live.find_key("__html").startswith("body{color:#000;background:#fff;")

    nextjs_org = BeautifulFD(nextjs_org_html)
    assert nextjs_org.find_key("b") == "4mSOwJptzzPemGzzI8AOo"
    styles = nextjs_org.find_key_all("style")
    assert {style for style in styles if isinstance(style, str)} == {"$undefined"}
    assert styles.count({"display": "inline-block"}) == 2

    assert BeautifulFD(mintstars_com_html).find_key("createdAt") == "$D2024-02-26T22:03:52.451Z"
