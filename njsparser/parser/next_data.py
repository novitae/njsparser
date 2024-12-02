import orjson

from ..utils import _supported_tree, make_tree

def find_nextdata(value: _supported_tree):
    if len(nextdata := make_tree(value=value).xpath(".//script[@id='__NEXT_DATA__']/text()")):
        assert len(nextdata) == 1, f"invalid {len(nextdata)=}"
        return orjson.loads(nextdata.pop().strip())