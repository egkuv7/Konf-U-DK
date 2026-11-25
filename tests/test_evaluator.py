"""Модульные тесты вычисления значений и констант.

Покрыты все конструкции варианта 15: числа, строки, массивы,
словари, однострочные и многострочные комментарии, объявления
констант и обращения к ним, а также вложенность конструкций.
"""

import unittest

from src.evaluator import evaluate_tree
from src.parser import parse_config


def evaluate_text(text):
    """Разобрать текст конфигурации и вычислить его значения."""
    return evaluate_tree(parse_config(text), {})


class TestScalars(unittest.TestCase):
    """Тесты чисел и строк."""

    def test_number(self):
        """Целое число вычисляется в значение типа int."""
        self.assertEqual(evaluate_text("42"), [42])

    def test_zero(self):
        """Ноль допускается форматом чисел варианта."""
        self.assertEqual(evaluate_text("0"), [0])

    def test_big_number(self):
        """Длинное число не теряет разряды."""
        self.assertEqual(evaluate_text("1234567890"), [1234567890])

    def test_string(self):
        """Строка освобождается от обрамляющих кавычек."""
        self.assertEqual(evaluate_text('"Это строка"'), ["Это строка"])

    def test_empty_string(self):
        """Пустая строка допустима."""
        self.assertEqual(evaluate_text('""'), [""])

    def test_comment_marks_inside_string(self):
        """Символы -- внутри строки не начинают комментарий."""
        self.assertEqual(evaluate_text('"a -- b"'), ["a -- b"])

    def test_several_values(self):
        """Значения верхнего уровня сохраняют порядок следования."""
        self.assertEqual(evaluate_text('1 "два" 3'), [1, "два", 3])


class TestArrays(unittest.TestCase):
    """Тесты массивов, включая вложенные."""

    def test_flat_array(self):
        """Массив чисел вычисляется в список."""
        self.assertEqual(evaluate_text("(1, 2, 3)"), [[1, 2, 3]])

    def test_single_item(self):
        """Массив из одного элемента не требует запятой."""
        self.assertEqual(evaluate_text("(7)"), [[7]])

    def test_empty_array(self):
        """Пустой массив вычисляется в пустой список."""
        self.assertEqual(evaluate_text("()"), [[]])

    def test_mixed_types(self):
        """Массив содержит значения разных типов."""
        self.assertEqual(evaluate_text('(1, "два")'), [[1, "два"]])

    def test_nested_arrays(self):
        """Вложенные массивы сохраняют структуру."""
        text = "((1, 2), (3, (4, 5)))"
        self.assertEqual(evaluate_text(text), [[[1, 2], [3, [4, 5]]]])

    def test_array_of_dicts(self):
        """Массив словарей вычисляется в список словарей."""
        text = "([A => 1], [B => 2])"
        self.assertEqual(evaluate_text(text), [[{"A": 1}, {"B": 2}]])


class TestDicts(unittest.TestCase):
    """Тесты словарей и имён ключей."""

    def test_flat_dict(self):
        """Словарь вычисляется в отображение имён на значения."""
        text = '[HOST => "localhost", PORT => 5432]'
        expected = [{"HOST": "localhost", "PORT": 5432}]
        self.assertEqual(evaluate_text(text), expected)

    def test_empty_dict(self):
        """Пустой словарь вычисляется в пустое отображение."""
        self.assertEqual(evaluate_text("[]"), [{}])

    def test_name_with_underscore(self):
        """Имя может начинаться с подчёркивания."""
        self.assertEqual(evaluate_text("[_X1 => 1]"), [{"_X1": 1}])

    def test_name_with_digits(self):
        """Имя содержит цифры после первого символа."""
        self.assertEqual(evaluate_text("[A1B2 => 0]"), [{"A1B2": 0}])

    def test_nested_dict(self):
        """Словари вкладываются друг в друга."""
        text = "[A => [B => [C => 1]]]"
        self.assertEqual(evaluate_text(text), [{"A": {"B": {"C": 1}}}])

    def test_dict_with_array(self):
        """Значением словаря может быть массив."""
        text = "[LIST => (1, 2)]"
        self.assertEqual(evaluate_text(text), [{"LIST": [1, 2]}])


class TestComments(unittest.TestCase):
    """Тесты однострочных и многострочных комментариев."""

    def test_single_line(self):
        """Однострочный комментарий игнорируется."""
        self.assertEqual(evaluate_text("-- пояснение\n42"), [42])

    def test_multi_line(self):
        """Многострочный комментарий игнорируется целиком."""
        text = "#| первая\nвторая строка |#\n42"
        self.assertEqual(evaluate_text(text), [42])

    def test_comment_inside_dict(self):
        """Комментарий между элементами словаря допустим."""
        text = "[A => 1, -- пояснение\nB => 2]"
        self.assertEqual(evaluate_text(text), [{"A": 1, "B": 2}])

    def test_comment_inside_array(self):
        """Многострочный комментарий внутри массива допустим."""
        text = "(1, #| пояснение |# 2)"
        self.assertEqual(evaluate_text(text), [[1, 2]])

    def test_only_comments(self):
        """Текст из одних комментариев не содержит значений."""
        self.assertEqual(evaluate_text("-- пусто\n#| пусто |#"), [])


class TestConstants(unittest.TestCase):
    """Тесты объявлений констант и обращений к ним."""

    def test_definition_only(self):
        """Объявление константы не попадает в результат."""
        self.assertEqual(evaluate_text("(def N 10);"), [])

    def test_constant_use(self):
        """Обращение к константе возвращает её значение."""
        self.assertEqual(evaluate_text("(def N 10); ?{N}"), [10])

    def test_constant_in_array(self):
        """Константа вычисляется внутри массива."""
        text = "(def N 5); (1, ?{N}, 3)"
        self.assertEqual(evaluate_text(text), [[1, 5, 3]])

    def test_constant_in_dict(self):
        """Константа вычисляется в значении словаря."""
        text = '(def S "текст"); [A => ?{S}]'
        self.assertEqual(evaluate_text(text), [{"A": "текст"}])

    def test_constant_array(self):
        """Константой может быть массив."""
        text = "(def A (1, 2)); ?{A}"
        self.assertEqual(evaluate_text(text), [[1, 2]])

    def test_constant_dict(self):
        """Константой может быть словарь."""
        text = "(def D [X => 1]); ?{D}"
        self.assertEqual(evaluate_text(text), [{"X": 1}])

    def test_constant_from_constant(self):
        """Константа ссылается на ранее объявленную константу."""
        text = "(def A 1); (def B ?{A}); ?{B}"
        self.assertEqual(evaluate_text(text), [1])

    def test_redefinition(self):
        """Повторное объявление заменяет значение константы."""
        text = "(def A 1); (def A 2); ?{A}"
        self.assertEqual(evaluate_text(text), [2])

    def test_constant_in_nested_structure(self):
        """Константа вычисляется на любой глубине вложенности."""
        text = "(def N 9); [A => (1, [B => ?{N}])]"
        expected = [{"A": [1, {"B": 9}]}]
        self.assertEqual(evaluate_text(text), expected)


class TestConstantErrors(unittest.TestCase):
    """Тесты сообщений об ошибках константных вычислений."""

    def test_undefined_constant(self):
        """Необъявленная константа вызывает ValueError с именем."""
        with self.assertRaises(ValueError) as caught:
            evaluate_text("?{MISSING}")
        self.assertIn("MISSING", str(caught.exception))

    def test_use_before_definition(self):
        """Обращение до объявления является ошибкой."""
        with self.assertRaises(ValueError):
            evaluate_text("?{A} (def A 1);")

    def test_undefined_in_nested_value(self):
        """Ошибка обнаруживается во вложенном значении."""
        with self.assertRaises(ValueError):
            evaluate_text("[A => (1, ?{NOPE})]")


class TestContext(unittest.TestCase):
    """Тесты контекста, разделяемого между вызовами."""

    def test_context_is_filled(self):
        """Объявление пополняет переданный контекст."""
        context = {}
        evaluate_tree(parse_config("(def N 7);"), context)
        self.assertEqual(context, {"N": 7})

    def test_context_reuse(self):
        """Контекст сохраняется между разборами двух текстов."""
        context = {}
        evaluate_tree(parse_config("(def N 7);"), context)
        tree = parse_config("?{N}")
        self.assertEqual(evaluate_tree(tree, context), [7])


if __name__ == "__main__":
    unittest.main()
