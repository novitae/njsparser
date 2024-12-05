from njsparser.tools import (
    has_nextjs,
    find_build_id,
    filter_flight_data,
)
from njsparser.parser.types import FlightSpecialData, FlightError, FlightDataContainer

from . import *

def test_has_nextjs():
    assert has_nextjs(value=m_soundcloud_com_html) is True
    assert has_nextjs(value=nextjs_org_html) is True
    assert has_nextjs(value=x_com_html) is False

def test_find_build_id():
    assert find_build_id(value=m_soundcloud_com_html) == "1733156665"
    assert find_build_id(value=nextjs_org_html) == "4mSOwJptzzPemGzzI8AOo"
    assert find_build_id(value=x_com_html) is None
    assert find_build_id(value=swag_live_html) == "giz3a1H7OUzfxgxRHIdMx"

def test_filter_flight_data():
    err = FlightError(value={"digest": "NEXT_NOT_FOUND"}, value_class=None, index=1)
    spe = FlightSpecialData(value="$Sreactblahblah", value_class=None, index=2)
    items = [err, spe]
    flight_data = {item.index: item for item in items}
    assert filter_flight_data(flight_data=flight_data, class_filters=[]) == items
    assert filter_flight_data(flight_data=flight_data, class_filters=[FlightError]) == [err]
    assert filter_flight_data(flight_data=flight_data, class_filters=[FlightSpecialData]) == [spe]
    assert filter_flight_data(flight_data=flight_data, class_filters=[FlightDataContainer]) == []
