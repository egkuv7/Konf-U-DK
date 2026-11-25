"""Модуль синтаксического анализа учебного конфигурационного языка.
"""
from lark import Lark

GRAMMAR = r"""
start: (def_stmt | expr)*
def_stmt: "(" "def" NAME expr ")" ";"
?expr: dict | array | ESCAPED_STRING | NUMBER | var_ref
dict: "[" (dict_item ("," dict_item)*)? "]"
dict_item: NAME "=>" expr
array: "(" (expr ("," expr)*)? ")"
var_ref: "?{" NAME "}"
NAME: /[_A-Z][_a-zA-Z0-9]*/
NUMBER: /\d+/
COMMENT_SINGLE: /--[^\n]*/
COMMENT_MULTI: /#\|[\s\S]*?\|#/
%import common.ESCAPED_STRING
%import common.WS
%ignore WS
%ignore COMMENT_SINGLE
%ignore COMMENT_MULTI
"""

def get_parser():
    """Создать и вернуть синтаксический анализатор Lark."""
    return Lark(
        GRAMMAR,
        parser="earley",
        propagate_positions=True,
        maybe_placeholders=False,
    )

def parse_config(text):
    """Разобрать текст конфигурации и вернуть дерево разбора."""
    return get_parser().parse(text)
