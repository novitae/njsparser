from njsparser.parser.flight_data import parse_decoded_raw_flight_data
from njsparser.parser.references import resolve_references, iter_key
from njsparser.parser.types import DataContainer, DataParent

_rows = parse_decoded_raw_flight_data(decoded_raw_flight_data=[
    '1:I[30777,["71523","static/chunks/a.js"],"default"]\n',
    '2:T5,hello',
    '3:{"make":"MAZDA","description":"$2"}\n',
    '4:["$","$L1",null,{"listing":"$3","seller":{"name":"Garage"}}]\n',
    '5:["$","p",null,{"children":"later"}]\n',
    '6:{"price":100}\n',
    '7:{"self":"$7"}\n',
    '8:["$","$L1",null,{"children":["$","$L1",null,{"car":{"id":1}}]}]\n',
    '9:[["$","div",null,{"car":{"id":2}}],["$","div",null,{}]]\n',
    'a:{"page":"$Lb"}\n',
    'b:{"car":{"id":3}}\n',
])

def test_resolve_references_to_a_row():
    assert resolve_references("$6", _rows) == {"price": 100}
    assert resolve_references("$2", _rows) == "hello"
    assert resolve_references({"cars": ["$6", "$6"]}, _rows) == {"cars": [{"price": 100}, {"price": 100}]}

def test_resolve_references_inside_a_referenced_row():
    assert resolve_references("$3", _rows) == {"make": "MAZDA", "description": "hello"}

def test_resolve_references_of_an_element():
    assert resolve_references(_rows[4], _rows) == [
        "$", "$L1", None, {
            "listing": {"make": "MAZDA", "description": "hello"},
            "seller": {"name": "Garage"},
        },
    ]

def test_resolve_references_with_a_path():
    assert resolve_references("$4:props:seller", _rows) == {"name": "Garage"}
    assert resolve_references("$4:props:seller:name", _rows) == "Garage"
    assert resolve_references("$4:type", _rows) == "$L1"
    assert resolve_references("$4:props:listing", _rows) == {"make": "MAZDA", "description": "hello"}

def test_resolve_references_with_a_path_through_elements():
    assert isinstance(_rows[8], DataParent)
    assert resolve_references("$8:props:children:props:car", _rows) == {"id": 1}
    assert isinstance(_rows[9], DataContainer)
    assert resolve_references("$9:0:props:car", _rows) == {"id": 2}

def test_resolve_references_with_a_path_through_a_reference():
    assert resolve_references("$4:props:listing:make", _rows) == "MAZDA"
    assert resolve_references("$a:page:car", _rows) == {"id": 3}

def test_resolve_references_to_a_later_row():
    assert resolve_references({"later": "$L5", "promise": "$@6"}, _rows) == {
        "later": ["$", "p", None, {"children": "later"}],
        "promise": {"price": 100},
    }

def test_resolve_references_keeps_other_strings():
    kept = {
        "module": "$L1",
        "missing_row": "$ff",
        "missing_path": "$4:props:nope",
        "index_out_of_range": "$9:5",
        "undefined": "$undefined",
        "date": "$D2024-12-07T14:46:45.389Z",
        "symbol": "$Sreact.suspense",
        "escaped": "$$3",
        "text": "3",
    }
    assert resolve_references(kept, _rows) == kept

def test_resolve_references_keeps_a_cycle():
    assert resolve_references("$7", _rows) == {"self": "$7"}

def test_resolve_references_returns_a_copy():
    resolved = resolve_references(_rows[3], _rows)
    resolved["make"] = "FIAT"
    assert _rows[3].value == {"make": "MAZDA", "description": "$2"}

def test_iter_key():
    value = {
        "car": {"id": 1, "car": {"id": 2}},
        "cars": [{"car": {"id": 3}}, "car"],
        "id": 4,
    }
    assert list(iter_key(value, "car")) == [{"id": 1, "car": {"id": 2}}, {"id": 2}, {"id": 3}]
    assert list(iter_key(value, "id")) == [4, 1, 2, 3]
    assert list(iter_key(value, "nope")) == []

def test_iter_key_through_elements():
    assert list(iter_key(_rows[8], "car")) == [{"id": 1}]
    assert list(iter_key(_rows[9], "car")) == [{"id": 2}]
