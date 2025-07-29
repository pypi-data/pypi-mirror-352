# orlang/transpiler.py
from lark import Transformer


class OrlangToPython(Transformer):
    def __init__(self):
        self.code_lines = []

    def start(self, items):
        return "\n".join(items)

    def statement(self, items):
        return items[0]

    def var_decl(self, items):
        name, value = items[0], items[1]
        return f"{name} = {value}"

    def assignment(self, items):
        # Filter out any non-string tokens (like semicolons)
        filtered = [item for item in items if isinstance(item, str)]
        return filtered[0]

    def print_stmt(self, items):
        return f"print({items[0]})"

    def if_stmt(self, items):
        condition, true_block, *false_block = items
        result = f"if {condition}:\n{true_block}"
        if false_block:
            result += f"\nelse:\n{false_block[0]}"
        return result

    def while_stmt(self, items):
        condition, body = items
        return f"while {condition}:\n{body}"

    def block(self, items):
        # Filter out semicolons and other non-string tokens
        lines = [line for line in items if isinstance(line, str) and line.strip()]
        return "\n".join(f"    {line}" for line in lines)

    # Handle bare assignments
    def assign_expr(self, items):
        # The items list contains: [name, value]
        name = items[0]
        value = items[1]
        return f"{name} = {value}"

    # for‐loop init
    def for_var_decl(self, items):
        name, value = items
        return f"{name} = {value}"

    def for_assignment(self, items):
        # reuse assign_expr logic
        return self.assign_expr(items)

    def for_init_empty(self, items):
        return ""

    # for‐loop update
    def for_update(self, items):
        # items[0] is the string returned by assign_expr
        return items[0]

    def for_stmt(self, items):
        # The items list contains: [init, semicolon, condition, semicolon, update, block]
        init = items[0]
        condition = items[2]
        update = items[4]
        block = items[5]

        # Convert tree nodes to strings if they aren't already
        init = str(init) if init else ""
        update = str(update) if update else ""

        # strip any trailing semicolons
        if init.endswith(";"):
            init = init[:-1]
        if update.endswith(";"):
            update = update[:-1]

        # ensure block is a list of lines
        lines = block.splitlines() if isinstance(block, str) else block

        # construct Python‐style for‐loop via while‐loop
        # Note: update statement needs to be indented to match the block
        return f"{init}\nwhile {condition}:\n" + self.indent(lines + [update])

    @staticmethod
    def indent(lines):
        if isinstance(lines, str):
            lines = lines.splitlines()
        # Ensure each line has exactly 4 spaces of indentation
        return '\n'.join("    " + line.lstrip() for line in lines)


    # Expressions
    def add(self, items):
        return f"({items[0]} + {items[1]})"

    def sub(self, items):
        return f"({items[0]} - {items[1]})"

    def mul(self, items):
        return f"({items[0]} * {items[1]})"

    def div(self, items):
        return f"({items[0]} / {items[1]})"

    def eq(self, items):
        return f"({items[0]} == {items[1]})"

    def neq(self, items):
        return f"({items[0]} != {items[1]})"

    def lt(self, items):
        return f"({items[0]} < {items[1]})"

    def gt(self, items):
        return f"({items[0]} > {items[1]})"

    def lte(self, items):
        return f"({items[0]} <= {items[1]})"

    def gte(self, items):
        return f"({items[0]} >= {items[1]})"

    def and_expr(self, items):
        return f"({items[0]} and {items[1]})"

    def or_expr(self, items):
        return f"({items[0]} or {items[1]})"

    # Literals
    def number(self, items):
        return str(items[0])

    def string(self, items):
        return items[0]

    def true(self, _):
        return "True"

    def false(self, _):
        return "False"

    def null(self, _):
        return "None"

    def var(self, items):
        return str(items[0])
