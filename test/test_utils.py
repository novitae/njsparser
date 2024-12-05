from njsparser.utils import join, make_tree, etree
import pytest

def test_make_tree():
    h = "<html>hello</html>"
    assert isinstance(make_tree(value=h.encode()), etree._Element)
    assert isinstance((result := make_tree(value=h)), etree._Element)
    assert isinstance(make_tree(value=result), etree._Element)
    with pytest.raises(TypeError):
        make_tree(value=1)

def test_join():
    assert join("hello", "world") == "/hello/world"
    assert join("/hello///", "/world/") == "/hello/world"
    