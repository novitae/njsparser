from typing import Any, Dict, Optional

class _Undefined:
    """Represents a JS `undefined` value."""
    def __repr__(self) -> str:
        return "Undefined"

Undefined = _Undefined()

class Parser:
    """A JSON-like parser that supports `undefined` and `void 0` values,
    variable substitutions, and unquoted object keys.

    Args:
        src (str): The source string to parse.
        kwargs (dict, optional): A dictionary of arguments for variable substitution.
    """

    def __init__(
        self,
        src: str,
        kwargs: Optional[Dict[str, Any]] = None,
        raise_on_excess_data: bool = None,
    ) -> None:
        self.src: str = src
        self.index: int = 0
        self.kwargs: Dict[str, Any] = kwargs or {}

    def eof(self) -> bool:
        """
        Checks if the parser has reached the end of the source string.

        Returns:
            bool: True if end of file is reached, False otherwise.
        """
        return self.index >= len(self.src)

    def peek_one(self) -> str:
        """
        Returns the next character without consuming it.

        Raises:
            ValueError: If the end of input is reached.

        Returns:
            str: The next character.
        """
        if self.eof():
            raise ValueError("Unexpected end of input while peeking")
        return self.src[self.index]

    def consume_one(self) -> str:
        """
        Consumes the next character and advances the index.

        Raises:
            ValueError: If the end of input is reached.

        Returns:
            str: The consumed character.
        """
        if self.eof():
            raise ValueError("Unexpected end of input while consuming one character")
        char = self.src[self.index]
        self.index += 1
        return char

    def consume_n(self, n: int) -> str:
        """
        Consumes the next `n` characters and advances the index.

        Args:
            n (int): Number of characters to consume.

        Raises:
            ValueError: If the end of input is reached before consuming `n` characters.

        Returns:
            str: The consumed substring.
        """
        if self.index + n > len(self.src):
            raise ValueError(f"Unexpected end of input while consuming {n} characters")
        result = self.src[self.index:self.index + n]
        self.index += n
        return result

    def test(self, what: str) -> bool:
        """
        Checks if the upcoming characters match the given string.

        Args:
            what (str): The string to test.

        Returns:
            bool: True if the string matches, False otherwise.
        """
        return self.src[self.index:].startswith(what)

    def consume(self, what: str) -> str:
        """
        Consumes the given string if it matches the input.

        Args:
            what (str): The string to consume.

        Raises:
            ValueError: If the string does not match.

        Returns:
            str: The consumed string.
        """
        if not self.test(what):
            raise ValueError(f'Expected "{what}" but found "{self.src[self.index:self.index + len(what)]}" at index {self.index}')
        self.index += len(what)
        return what

    def try_consume(self, what: str) -> Optional[str]:
        """
        Tries to consume the given string if it matches the input.

        Args:
            what (str): The string to consume.

        Returns:
            Optional[str]: The consumed string if successful, otherwise None.
        """
        if self.test(what):
            self.index += len(what)
            return what
        return None

    def skip_spaces(self) -> None:
        """
        Skips whitespace characters in the input.
        """
        while not self.eof() and self.src[self.index].isspace():
            self.index += 1

    def value(self) -> Any:
        """
        Parses a value from the input.

        Raises:
            ValueError: If an unexpected character is encountered.

        Returns:
            Any: The parsed value.
        """
        self.skip_spaces()
        t = self.peek_one()

        if t == '{':
            return self.object()
        elif t == '[':
            return self.array('[', ']')
        elif t in ('"', "'"):
            return self.string()
        elif t.isdigit() or t in ('-', '.'):
            return self.number()
        elif self.try_consume('null') is not None:
            return None
        elif self.try_consume('true') is not None:
            return True
        elif self.try_consume('false') is not None:
            return False
        elif self.try_consume('!1') is not None:
            return False
        elif self.try_consume('void 0') is not None:
            return Undefined
        elif self.try_consume('undefined') is not None:
            return Undefined
        else:
            if (vn := self.var_name()) in self.kwargs:
                return self.kwargs[vn]
            else:
                raise ValueError(f"Syntax error: unexpected character '{t}' at index {self.index}")

    def object_key(self) -> str:
        """
        Parses an object key.

        Returns:
            str: The parsed object key.
        """
        self.skip_spaces()
        if self.test(('"', "'")):
            result = self.string()
        else:
            result = self.var_name()
        self.skip_spaces()
        return result

    def object(self) -> Dict[str, Any]:
        """
        Parses an object from the input.

        Returns:
            dict: The parsed object.
        """
        self.consume('{')
        result = {}
        while self.peek_one() != '}':
            key = self.object_key()
            self.consume(':')
            value = self.value()
            result[key] = value
            self.skip_spaces()
            if self.peek_one() == '}':
                break
            self.consume(',')
        self.skip_spaces()
        self.consume('}')
        return result

    def array(self, opener: str, closer: str) -> list:
        """
        Parses an array or tuple from the input.

        Args:
            opener (str): The opening bracket or parenthesis.
            closer (str): The closing bracket or parenthesis.

        Returns:
            list: The parsed array or tuple.
        """
        self.consume(opener)
        result = []
        while self.peek_one() != closer:
            result.append(self.value())
            self.skip_spaces()
            if not self.try_consume(','):
                break
        self.skip_spaces()
        self.consume(closer)
        return result

    def string(self) -> str:
        """
        Parses a string value.

        Returns:
            str: The parsed string.
        """
        delim = self.consume_one()
        result = ""
        while self.peek_one() != delim:
            c = self.consume_one()
            if c == "\\":
                c = self.consume_one()
                if c == 'n':
                    c = '\n'
                elif c == 'r':
                    c = '\r'
                elif c == 't':
                    c = '\t'
                elif c == 'u':
                    hex_str = self.consume_n(4)
                    c = chr(int(hex_str, 16))
            result += c
        self.consume(delim)
        return result

    def var_name(self) -> str:
        """
        Parses a variable name.

        Returns:
            str: The parsed variable name.
        """
        result = ""
        while (p := self.peek_one()).isalnum() or p in "_$":
            c = self.consume_one()
            result += c
        return result

    def number(self) -> float:
        """
        Parses a number.

        Returns:
            float: The parsed number.

        Raises:
            ValueError: If no valid number is found.
        """
        str_num = ""
        integer = True
        if self.peek_one() == '-':
            str_num += self.consume_one()
        while not self.eof() and self.peek_one().isdigit():
            str_num += self.consume_one()
        if not self.eof() and self.peek_one() == '.':
            integer = False
            str_num += self.consume_one()
            while not self.eof() and self.peek_one().isdigit():
                str_num += self.consume_one()
        if not self.eof() and self.peek_one().lower() == 'e':
            integer = False
            str_num += self.consume_one()
            if not self.eof() and self.peek_one() in ('-', '+'):
                str_num += self.consume_one()
            while not self.eof() and self.peek_one().isdigit():
                str_num += self.consume_one()
        if not str_num:
            raise ValueError(f'Expected number but found "{self.peek_one()}" at index {self.index}')
        return int(str_num) if integer else float(str_num)

    def loads(self, raise_on_excess_data: bool = None) -> Any:
        """
        Parses the entire source string as a JSON-like document.

        Args:
            raise_on_excess_data (bool, optional): Do we raise if we found more data after
                finished the parsing ?

        Returns:
            Any: The parsed value.

        Raises:
            ValueError: If excess data is found after parsing.
        """
        value = self.value()
        self.skip_spaces()
        if raise_on_excess_data is True and self.eof() is False:
            raise ValueError(f"Excess data at end of JSON document starting at index {self.index}")
        return value
    
def loads(
    string: str,
    kwargs: Optional[Dict[str, Any]] = None,
    raise_on_excess_data: bool = None,
):
    """Parses a json-like coming from javascript.
    
    Args:
        src (str): The source string to parse.
        kwargs (dict, optional): A dictionary of arguments for variable substitution.
        raise_on_excess_data (bool, optional): Do we raise if we found more data after
            finished the parsing ?

    Returns:
        Any: A json data.
    """
    parser = Parser(src=string, kwargs=kwargs)
    return parser.loads(raise_on_excess_data=raise_on_excess_data)