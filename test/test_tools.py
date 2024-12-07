from njsparser.tools import (
    has_nextjs,
    findall_in_flight_data,
    find_in_flight_data,
    find_build_id,
)
from njsparser.parser.types import *

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

def test_find_in_flight_data():
    assert find_in_flight_data(flight_data, [URLQuery]) is None
    assert find_in_flight_data(flight_data, [RSCPayload]) == flight_data[0]
    assert find_in_flight_data(None) is None

def test_find_build_id():
    assert find_build_id(value=m_soundcloud_com_html) == "1733156665"
    assert find_build_id(value=nextjs_org_html) == "4mSOwJptzzPemGzzI8AOo"
    assert find_build_id(value=x_com_html) is None
    assert find_build_id(value=swag_live_html) == "giz3a1H7OUzfxgxRHIdMx"
    
    # Recursive search here
    assert find_build_id(value=club_fans_html) == "n2xbxZXkzoS6U5w7CgB-T"