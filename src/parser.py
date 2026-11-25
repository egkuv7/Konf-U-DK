"""Модуль для синтаксического анализа пользовательского языка конфигурации."""
from lark import Lark

GRAMMAR = r"""
start: (def_stmt | expr)*
def_stmt: "(" DEF NAME expr ")" ";"
expr: dict | array | string | NUMBER | var_ref
dict: "[" (dict_item ("," dict_item)*)? "]"
dict_item: NAME "=>" expr
array: "(" (expr ("," expr)*)? ")"
string: ESCAPED_STRING
var_ref: "?{" NAME "}"
DEF: "def"
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
    """Инициализировать и вернуть парсер Lark."""
    return Lark(
        GRAMMAR,
        parser="earley",
        propagate_positions=True
    )


def parse_config(text):
    """Разобрать входной текст в синтаксическое дерево Lark."""
    parser = get_parser()
    return parser.parse(text)
