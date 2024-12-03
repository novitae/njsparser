from njsparser.parser.next_data import get_next_data

from .. import *

def test_find_nextdata():
    assert get_next_data(value=m_soundcloud_com_html) is not None
    assert get_next_data(value=x_com_html) is None
    assert get_next_data(value=nextjs_org_html) is None