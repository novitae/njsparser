from njsparser.parser.urls import get_next_static_urls, get_base_path
import pytest

from .. import *

def test_get_next_static_urls():
    assert get_next_static_urls(value=m_soundcloud_com_html) is not None
    assert get_next_static_urls(value=x_com_html) is None
    assert get_next_static_urls(value=nextjs_org_html) is not None

def test_get_base_path():
    assert get_base_path(value=m_soundcloud_com_html) == "https://m.sndcdn.com"
    assert get_base_path(value=m_soundcloud_com_html, remove_domain=True) == ""
    assert get_base_path(value=x_com_html) is None
    assert get_base_path( value=["https://test.com/hello/_next/static/"] * 5,
                          remove_domain=True, ) == "/hello"
    with pytest.raises(AssertionError):
        # Doesn't contain any `/_next/static/`.
        get_base_path(value=["https://test.com/hello"])
    with pytest.raises(AssertionError):
        # The position of `/_next/static/` isn't the same.
        get_base_path(value=["/bubu/_next/static/", "/bububu/_next/static/"])