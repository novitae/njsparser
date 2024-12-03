from njsparser.tools import has_nextjs, find_build_id

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