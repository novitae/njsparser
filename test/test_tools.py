from njsparser.tools import (
    has_nextjs,
    findall_in_flight_data,
    find_in_flight_data,
    find_build_id,
    BeautifulFD,
    resolve_type,
)
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