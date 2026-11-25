"""Модуль для оценки синтаксического дерева и разрешения констант."""
from lark import Tree, Token


def evaluate_tree(tree, context):
    """Вычислить дерево разбора и вернуть список значений."""
    results = []
    for child in tree.children:
        if isinstance(child, Tree) and child.data == "def_stmt":
            eval_def(child, context)
        else:
            results.append(eval_expr(child, context))
    return results


def eval_def(node, context):
    """Обработать объявление константы и пополнить контекст."""
    name = str(node.children[-2])
    context[name] = eval_expr(node.children[-1], context)

def eval_expr(node, context):
    """Вычислить значение узла выражения."""
    if isinstance(node, Token):
        return eval_token(node)
    return eval_node(node, context)


def eval_token(token):
    """Преобразовать токен Lark в примитив Python."""
    if token.type == "NUMBER":
        return int(token)
    if token.type == "ESCAPED_STRING":
        return str(token)[1:-1]
    return str(token)


def eval_node(node, context):
    """Оценить сложный узел дерева Lark."""
    if node.data == "var_ref":
        return resolve_var(node, context)
    if node.data == "dict":
        return eval_dict(node, context)
    if node.data == "array":
        return eval_array(node, context)
    return None


def resolve_var(node, context):
    """Разрешить ссылку на переменную из контекста."""
    name = str(node.children[0])
    if name not in context:
        raise ValueError(f"Undefined variable: {name}")
    return context[name]


def eval_dict(node, context):
    """Вычислить словарь в виде отображения имён на значения."""
    result = {}
    for item in node.children:
        key = str(item.children[-2])
        result[key] = eval_expr(item.children[-1], context)
    return result


def eval_array(node, context):
    """Оценить узел массива."""
    return [eval_expr(child, context) for child in node.children]
