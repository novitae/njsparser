from njsparser.parser.flight_data import (
    has_flight_data,
    get_raw_flight_data,
    get_flight_data
)

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