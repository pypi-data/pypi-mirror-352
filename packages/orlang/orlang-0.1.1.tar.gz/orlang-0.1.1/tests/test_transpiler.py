from orlang.parser import parser
from orlang.transpiler import OrlangToPython

def test_transpile_var_decl():
    code = 'bakka x = 10 + 5;'
    tree = parser.parse(code)
    transpiled = OrlangToPython().transform(tree)
    assert 'x = (10 + 5)' in transpiled

def test_transpile_if_else():
    code = '''
    yoo (x > 5) {
        barreessi "big";
    } kanbiroo {
        barreessi "small";
    }
    '''
    tree = parser.parse(code)
    transpiled = OrlangToPython().transform(tree)
    assert 'if (x > 5):' in transpiled
    assert 'print("big")' in transpiled
