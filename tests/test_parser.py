"""Тесты для модуля парсера."""
import unittest
from src.parser import parse_config


class TestParser(unittest.TestCase):
    """Тестовые примеры для синтаксического анализа."""

    def test_parse_number(self):
        """Тест на разбор простого числа."""
        tree = parse_config("42")
        self.assertIsNotNone(tree)

    def test_parse_string(self):
        """Тест на разбор строки."""
        tree = parse_config('"hello world"')
        self.assertIsNotNone(tree)

    def test_parse_comments(self):
        """Тест на игнорирование комментариев."""
        text = "-- single\n#| multi |#\n42"
        tree = parse_config(text)
        self.assertEqual(len(tree.children), 1)

    def test_parse_def(self):
        """Определение константы для проверки синтаксиса."""
        text = "(def MY_VAR 100);"
        tree = parse_config(text)
        self.assertEqual(tree.children[0].data, "def_stmt")
