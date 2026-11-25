"""Модуль для оценки синтаксического дерева и разрешения констант."""
from lark import Tree, Token


def evaluate_tree(tree, context):
    """Оценить синтаксическое дерево и вернуть список результатов."""
    results = []
    for child in tree.children:
        if child.data == "def_stmt":
            eval_def(child, context)
        else:
            val = eval_expr(child, context)
            results.append(val)
    return results


def eval_def(node, context):
    """Оценить оператор определения и обновить контекст."""
    name = str(node.children[0])
    value = eval_expr(node.children[1], context)
    context[name] = value


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
    """Оценить узел словаря."""
    result = {}
    for item in node.children:
        key = str(item.children[0])
        val = eval_expr(item.children[1], context)
        result[key] = val
    return result


def eval_array(node, context):
    """Оценить узел массива."""
    return [eval_expr(child, context) for child in node.children]
