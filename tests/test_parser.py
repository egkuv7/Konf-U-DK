"""Модульные тесты синтаксического анализатора варианта 15.

Проверяется разбор всех конструкций языка и выявление синтаксических
ошибок: числа, строки, массивы, словари, имена, комментарии,
объявления констант и обращения к ним.
"""

import unittest

from lark import Token
from lark.exceptions import UnexpectedInput

from src.parser import parse_config


def first_node(text):
    """Разобрать текст и вернуть первый узел верхнего уровня."""
    return parse_config(text).children[0]


class TestNumbers(unittest.TestCase):
    """Тесты разбора чисел."""

    def test_integer(self):
        """Целое число разбирается в токен NUMBER."""
        node = first_node("42")
        self.assertEqual(node.type, "NUMBER")
        self.assertEqual(str(node), "42")

    def test_zero(self):
        """Ноль соответствует шаблону чисел варианта."""
        self.assertEqual(str(first_node("0")), "0")

    def test_leading_zeros(self):
        """Ведущие нули допустимы шаблоном чисел варианта."""
        self.assertEqual(str(first_node("007")), "007")

    def test_scalar_is_token(self):
        """Скаляр верхнего уровня приходит токеном, а не узлом."""
        self.assertIsInstance(first_node("42"), Token)


class TestStrings(unittest.TestCase):
    """Тесты разбора строк."""

    def test_string_token(self):
        """Строка разбирается в токен ESCAPED_STRING."""
        self.assertEqual(first_node('"текст"').type, "ESCAPED_STRING")

    def test_empty_string(self):
        """Пустая строка допустима."""
        self.assertEqual(str(first_node('""')), '""')

    def test_cyrillic(self):
        """Кириллица внутри строки допустима."""
        self.assertEqual(str(first_node('"Это строка"')), '"Это строка"')

    def test_comment_marks_inside(self):
        """Символы -- внутри строки не начинают комментарий."""
        self.assertEqual(str(first_node('"a -- b"')), '"a -- b"')


class TestArrays(unittest.TestCase):
    """Тесты разбора массивов."""

    def test_array_node(self):
        """Массив разбирается в узел array."""
        self.assertEqual(first_node("(1, 2)").data, "array")

    def test_array_items(self):
        """Элементы массива становятся потомками узла."""
        node = first_node("(1, 2, 3)")
        values = [str(item) for item in node.children]
        self.assertEqual(values, ["1", "2", "3"])

    def test_single_item(self):
        """Массив из одного элемента не требует запятой."""
        self.assertEqual(first_node("(7)").data, "array")

    def test_empty_array(self):
        """Пустой массив не содержит потомков."""
        self.assertFalse(first_node("()").children)

    def test_nested_arrays(self):
        """Вложенный массив остаётся узлом array."""
        node = first_node("((1, 2), 3)")
        self.assertEqual(node.children[0].data, "array")


class TestDicts(unittest.TestCase):
    """Тесты разбора словарей."""

    def test_dict_node(self):
        """Словарь разбирается в узел dict."""
        self.assertEqual(first_node("[A => 1]").data, "dict")

    def test_dict_item(self):
        """Пара словаря разбирается в узел dict_item."""
        node = first_node("[A => 1]")
        self.assertEqual(node.children[0].data, "dict_item")

    def test_item_name_and_value(self):
        """Имя и значение пары доступны по отрицательным индексам."""
        item = first_node("[HOST => 80]").children[0]
        self.assertEqual(str(item.children[-2]), "HOST")
        self.assertEqual(str(item.children[-1]), "80")

    def test_empty_dict(self):
        """Пустой словарь не содержит потомков."""
        self.assertFalse(first_node("[]").children)

    def test_nested_dict(self):
        """Значением пары может быть словарь."""
        item = first_node("[A => [B => 1]]").children[0]
        self.assertEqual(item.children[-1].data, "dict")


class TestNames(unittest.TestCase):
    """Тесты шаблона имён варианта 15."""

    def test_uppercase_name(self):
        """Имя может состоять из заглавных букв."""
        item = first_node("[ABC => 1]").children[0]
        self.assertEqual(str(item.children[-2]), "ABC")

    def test_underscore_start(self):
        """Имя может начинаться с подчёркивания."""
        item = first_node("[_X => 1]").children[0]
        self.assertEqual(str(item.children[-2]), "_X")

    def test_digits_after_first(self):
        """Цифры допустимы после первого символа имени."""
        item = first_node("[A1B2 => 1]").children[0]
        self.assertEqual(str(item.children[-2]), "A1B2")

    def test_lowercase_tail(self):
        """Строчные буквы допустимы после заглавной первой."""
        item = first_node("[BgColor => 1]").children[0]
        self.assertEqual(str(item.children[-2]), "BgColor")


class TestComments(unittest.TestCase):
    """Тесты игнорирования комментариев."""

    def test_single_line(self):
        """Однострочный комментарий не попадает в дерево."""
        tree = parse_config("-- пояснение\n42")
        self.assertEqual([str(n) for n in tree.children], ["42"])

    def test_multi_line(self):
        """Многострочный комментарий не попадает в дерево."""
        tree = parse_config("#| первая\nвторая |#\n42")
        self.assertEqual([str(n) for n in tree.children], ["42"])

    def test_inside_structures(self):
        """Комментарии допустимы между элементами конструкций."""
        text = "[A => 1, -- пояснение\nB => 2]"
        self.assertEqual(first_node(text).data, "dict")

    def test_only_comments(self):
        """Текст из одних комментариев даёт пустое дерево."""
        self.assertFalse(parse_config("-- пусто\n#| пусто |#").children)


class TestConstants(unittest.TestCase):
    """Тесты объявлений констант и обращений к ним."""

    def test_def_node(self):
        """Объявление разбирается в узел def_stmt."""
        self.assertEqual(first_node("(def N 1);").data, "def_stmt")

    def test_def_name(self):
        """Имя константы доступно по отрицательному индексу."""
        node = first_node("(def DB_PORT 5432);")
        self.assertEqual(str(node.children[-2]), "DB_PORT")

    def test_def_complex_value(self):
        """Значением константы может быть любая конструкция."""
        node = first_node("(def A (1, [B => 2]));")
        self.assertEqual(node.children[-1].data, "array")

    def test_var_ref_node(self):
        """Обращение разбирается в узел var_ref с именем."""
        node = first_node("?{N}")
        self.assertEqual(node.data, "var_ref")
        self.assertEqual(str(node.children[0]), "N")


class TestNesting(unittest.TestCase):
    """Тесты вложенности и последовательности значений."""

    def test_deep_structure(self):
        """Смешанная вложенность разбирается без ошибок."""
        text = '[A => (1, [B => (2, "три")]), C => 4]'
        self.assertEqual(first_node(text).data, "dict")

    def test_several_values(self):
        """Несколько значений верхнего уровня сохраняются в дереве."""
        tree = parse_config("1 (2) [A => 3]")
        self.assertEqual(str(tree.children[0]), "1")
        self.assertEqual(tree.children[1].data, "array")
        self.assertEqual(tree.children[2].data, "dict")


class TestEmptyInput(unittest.TestCase):
    """Тесты пустого входного текста."""

    def test_empty_text(self):
        """Пустой текст разбирается в пустое дерево."""
        self.assertFalse(parse_config("").children)

    def test_whitespace_only(self):
        """Пробельный текст разбирается в пустое дерево."""
        self.assertFalse(parse_config("  \n\t\n").children)


class TestSyntaxErrors(unittest.TestCase):
    """Тесты выявления синтаксических ошибок с сообщениями."""

    def test_lowercase_key(self):
        """Ключ со строчной первой буквы отвергается."""
        with self.assertRaises(UnexpectedInput):
            parse_config('[bg => "#ffffff"]')

    def test_quoted_key(self):
        """Строка в позиции ключа словаря отвергается."""
        with self.assertRaises(UnexpectedInput):
            parse_config('["BG" => 1]')

    def test_lowercase_constant(self):
        """Имя константы со строчной буквы отвергается."""
        with self.assertRaises(UnexpectedInput):
            parse_config("(def port 80);")

    def test_digit_start_name(self):
        """Имя, начинающееся с цифры, отвергается."""
        with self.assertRaises(UnexpectedInput):
            parse_config("[1A => 1]")

    def test_curly_braces(self):
        """Фигурные скобки не являются словарём варианта."""
        with self.assertRaises(UnexpectedInput):
            parse_config("{A => 1}")

    def test_unclosed_dict(self):
        """Незакрытая квадратная скобка отвергается."""
        with self.assertRaises(UnexpectedInput):
            parse_config("[A => 1")

    def test_unclosed_array(self):
        """Незакрытая круглая скобка отвергается."""
        with self.assertRaises(UnexpectedInput):
            parse_config("(1, 2")

    def test_missing_comma(self):
        """Пропущенная запятая между парами отвергается."""
        with self.assertRaises(UnexpectedInput):
            parse_config("[A => 1 B => 2]")

    def test_missing_semicolon(self):
        """Объявление без точки с запятой отвергается."""
        with self.assertRaises(UnexpectedInput):
            parse_config("(def N 1)")

    def test_float_number(self):
        """Дробное число не входит в шаблон чисел варианта."""
        with self.assertRaises(UnexpectedInput):
            parse_config("1.5")

    def test_trailing_comma(self):
        """Висячая запятая перед закрывающей скобкой отвергается."""
        with self.assertRaises(UnexpectedInput):
            parse_config("(1, 2,)")

    def test_error_position(self):
        """Сообщение об ошибке содержит номер строки входа."""
        with self.assertRaises(UnexpectedInput) as caught:
            parse_config("[A => 1,\n1B => 2]")
        self.assertIn("line 2", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
