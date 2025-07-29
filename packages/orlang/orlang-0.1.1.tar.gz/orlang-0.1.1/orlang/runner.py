from orlang.parser import parser
from orlang.transpiler import OrlangToPython

def run_orlang(code: str):
    tree = parser.parse(code)
    transpiled = OrlangToPython().transform(tree)
    print("--------Transpiled Python code--------")
    print(transpiled)
    print("--------------------------------------")
    exec(transpiled, globals())
