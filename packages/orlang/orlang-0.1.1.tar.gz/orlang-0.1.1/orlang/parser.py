from lark import Lark, Transformer
from pathlib import Path

GRAMMAR_PATH = Path(__file__).parent / "grammar.lark"

with open(GRAMMAR_PATH) as f:
    grammar = f.read()

parser = Lark(grammar, parser="lalr", start="start", propagate_positions=True)
