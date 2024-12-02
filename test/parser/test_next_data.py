from njsparser.parser.next_data import find_nextdata

from .. import *

def test_find_nextdata():
    assert find_nextdata(value=m_soundcloud_com_html) is not None
    assert find_nextdata(value=x_com_html) is None
    assert find_nextdata(value=nextjs_org_html) is None