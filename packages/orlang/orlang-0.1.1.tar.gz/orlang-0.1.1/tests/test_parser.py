from orlang.parser import parser

def test_parser_simple():
    code = 'bakka x = 5;'
    tree = parser.parse(code)
    assert tree is not None
