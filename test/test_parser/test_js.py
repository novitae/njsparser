import pytest
from njsparser.parser.js import loads, Undefined

def test_basic_object():
    assert loads('{"key": "value"}') == {"key": "value"}
    assert loads('{key: "value"}') == {"key": "value"}  # Unquoted key
    assert loads('{key: value}', kwargs={"value": 42}) == {"key": 42}  # Variable substitution

def test_nested_objects():
    assert loads('{"outer": {"inner": "value"}}') == {"outer": {"inner": "value"}}
    assert loads('{"outer": {inner: value}}', kwargs={"value": 100}) == {"outer": {"inner": 100}}

def test_arrays():
    assert loads('["a", "b", "c"]') == ["a", "b", "c"]
    assert loads('[1, 2, 3]') == [1, 2, 3]
    assert loads('[1, {"key": "value"}, 3]') == [1, {"key": "value"}, 3]

def test_numbers():
    assert loads('42') == 42.0
    assert loads('-42') == -42.0
    assert loads('3.14') == 3.14
    assert loads('-3.14') == -3.14
    assert loads('2e3') == 2000.0
    assert loads('-2.5e-3') == -0.0025

def test_special_values():
    assert loads('null') is None
    assert loads('true') is True
    assert loads('false') is False
    assert loads('undefined') is Undefined
    assert loads('void 0') is Undefined

def test_strings():
    assert loads('"hello"') == "hello"
    assert loads("'world'") == "world"
    assert loads('"escape\\nchars"') == "escape\nchars"
    assert loads('"unicode\\u2764"') == "unicode❤"

def test_unquoted_keys():
    assert loads('{key: "value"}') == {"key": "value"}
    assert loads('{key_with_underscores: 123}') == {"key_with_underscores": 123}

def test_variable_substitution():
    assert loads('{key: value}', kwargs={"value": 42}) == {"key": 42}
    assert loads('[value, value]', kwargs={"value": "test"}) == ["test", "test"]
    assert loads('{$: [_]}', kwargs={"$": "dollar", "_": "underscore"}) == {"$": ["underscore"]}

def test_edge_cases():
    # Empty object and array
    assert loads('{}') == {}
    assert loads('[]') == []
    # Whitespace handling
    assert loads(' {  key  :   "value"  } ') == {"key": "value"}
    assert loads('[ 1 ,  2 ,  3 ]') == [1, 2, 3]
    # Unexpected characters
    with pytest.raises(ValueError):
        loads('{key: "value", unexpected}')
    with pytest.raises(ValueError):
        loads('{key: "value", :}')
    # Missing value
    with pytest.raises(ValueError):
        loads('{key: }')
    # Unclosed structures
    with pytest.raises(ValueError):
        loads('{"key": "value"')
    with pytest.raises(ValueError):
        loads('[1, 2, 3')

def test_undefined_handling():
    parsed = loads('[undefined, void 0, "defined"]')
    assert parsed[0] is Undefined
    assert parsed[1] is Undefined
    assert parsed[2] == "defined"

def test_complex_mixed():
    src = """
    {
        key1: "value1",
        key2: [1, 2, {nestedKey: true}],
        key3: null,
        key4: undefined,
        key5: value
    }
    """
    kwargs = {"value": 123}
    result = loads(src, kwargs=kwargs)
    assert result == {
        "key1": "value1",
        "key2": [1, 2, {"nestedKey": True}],
        "key3": None,
        "key4": Undefined,
        "key5": 123,
    }

def test_string_escaping():
    assert loads('"line1\\nline2"') == "line1\nline2"
    assert loads('"tab\\tcharacter"') == "tab\tcharacter"
    assert loads('"quote\\"inside"') == 'quote"inside'

def test_invalid_inputs():
    with pytest.raises(ValueError):
        loads('invalid')
    with pytest.raises(ValueError):
        loads('{"key"')  # Missing closing brace
    with pytest.raises(ValueError):
        loads('{key: value}', kwargs={})  # Variable `value` undefined

def test_excess_data():
    string = '{"hello": "world"}();'
    assert loads(string, raise_on_excess_data=False) == {"hello": "world"}
    with pytest.raises(ValueError):
        loads(string, raise_on_excess_data=True)

def test_exclamation_point():
    loads('{hello:!0,yoo:!1}')
    loads('[!   true, !     false, !       [1, 2, 3]]')