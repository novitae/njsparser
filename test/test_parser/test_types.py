from njsparser.parser.types import HeadLink
import pytest

def test_HeadLink():
    with pytest.raises(AssertionError):
        HeadLink(["hello"])
    hl1 = HeadLink([
        (href1 := "/_next/static/media/569ce4b8f30dc480-s.p.woff2"),
        (type_name1 := "font"),
        (attrs1 := {"crossOrigin": "", "type": "font/woff2"})
    ])
    assert hl1.href == href1
    assert hl1.type_name == type_name1
    assert hl1.attrs == attrs1
    hl2 = HeadLink([
        (href2 := "/_next/static/css/3a4b7cc0153d49b4.css?dpl=dpl_F2qLi1zuzNsnuiFMqRXyYU9dbJYw"),
        (type_name2 := "style")
    ])
    assert hl2.href == href2
    assert hl2.type_name == type_name2
    assert hl2.attrs is None