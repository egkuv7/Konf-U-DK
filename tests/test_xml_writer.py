"""Модульные тесты построения XML-документа.

Проверяются примитивы, массивы, словари, вложенность, пустые
контейнеры, порядок элементов и экранирование символов XML.
"""

import unittest
import xml.etree.ElementTree as ET

from src.evaluator import evaluate_tree
from src.parser import parse_config
from src.xml_writer import generate_xml


def build_root(values):
    """Построить XML и разобрать его обратно в дерево элементов."""
    return ET.fromstring(generate_xml(values))


class TestDocument(unittest.TestCase):
    """Тесты структуры документа в целом."""

    def test_output_type(self):
        """Генератор возвращает строку, а не байты."""
        self.assertIsInstance(generate_xml([1]), str)

    def test_root_tag(self):
        """Корневой элемент документа называется config."""
        self.assertEqual(build_root([1]).tag, "config")

    def test_empty_document(self):
        """Пустой набор значений даёт пустой корневой элемент."""
        self.assertEqual(len(build_root([])), 0)

    def test_entry_per_value(self):
        """Каждое значение верхнего уровня даёт элемент entry."""
        root = build_root([1, "два", 3])
        expected = ["entry", "entry", "entry"]
        self.assertEqual([child.tag for child in root], expected)


class TestPrimitives(unittest.TestCase):
    """Тесты чисел и строк в XML."""

    def test_number(self):
        """Число записывается текстом элемента."""
        self.assertEqual(build_root([42])[0].text, "42")

    def test_zero(self):
        """Ноль не теряется при сериализации."""
        self.assertEqual(build_root([0])[0].text, "0")

    def test_string(self):
        """Строка записывается без обрамляющих кавычек."""
        self.assertEqual(build_root(["текст"])[0].text, "текст")

    def test_empty_string(self):
        """Пустая строка даёт элемент без текстового узла."""
        self.assertEqual(build_root([""])[0].text or "", "")


class TestArrays(unittest.TestCase):
    """Тесты массивов в XML."""

    def test_item_tags(self):
        """Элементы массива получают одинаковый тег item."""
        entry = build_root([[1, 2, 3]])[0]
        expected = ["item", "item", "item"]
        self.assertEqual([item.tag for item in entry], expected)

    def test_array_values(self):
        """Значения элементов массива сохраняются по порядку."""
        entry = build_root([[1, 2]])[0]
        self.assertEqual([item.text for item in entry], ["1", "2"])

    def test_empty_array(self):
        """Пустой массив даёт элемент без дочерних узлов."""
        self.assertEqual(len(build_root([[]])[0]), 0)

    def test_nested_array(self):
        """Вложенный массив оборачивается в отдельный item."""
        entry = build_root([[1, [2, 3]]])[0]
        self.assertEqual(entry[0].text, "1")
        self.assertEqual(entry[1][0].text, "2")
        self.assertEqual(entry[1][1].text, "3")


class TestDicts(unittest.TestCase):
    """Тесты словарей в XML."""

    def test_flat_dict(self):
        """Ключи словаря становятся тегами дочерних элементов."""
        entry = build_root([{"HOST": "localhost", "PORT": 5432}])[0]
        self.assertEqual(entry.find("HOST").text, "localhost")
        self.assertEqual(entry.find("PORT").text, "5432")

    def test_empty_dict(self):
        """Пустой словарь даёт элемент без дочерних узлов."""
        self.assertEqual(len(build_root([{}])[0]), 0)

    def test_nested_dict(self):
        """Вложенный словарь становится поддеревом элементов."""
        root = build_root([{"A": {"B": 1}}])
        self.assertEqual(root.find("entry/A/B").text, "1")

    def test_dict_inside_array(self):
        """Словарь внутри массива оборачивается в item."""
        root = build_root([[{"A": 1}]])
        self.assertEqual(root.find("entry/item/A").text, "1")

    def test_array_inside_dict(self):
        """Массив внутри словаря даёт последовательность item."""
        root = build_root([{"LIST": [1, 2]}])
        items = root.findall("entry/LIST/item")
        self.assertEqual([item.text for item in items], ["1", "2"])


class TestEscaping(unittest.TestCase):
    """Тесты экранирования специальных символов XML."""

    def test_special_characters(self):
        """Символы амперсанда и скобок экранируются."""
        xml = generate_xml(["a & b < c > d"])
        self.assertIn("&amp;", xml)
        self.assertIn("&lt;", xml)
        self.assertIn("&gt;", xml)

    def test_roundtrip_text(self):
        """После разбора XML исходный текст восстанавливается."""
        text = 'ООО "Ромашка" & Ко <тест>'
        self.assertEqual(build_root([text])[0].text, text)

    def test_cyrillic_values(self):
        """Кириллица сохраняется без перекодировки."""
        self.assertEqual(build_root(["привет"])[0].text, "привет")


class TestIntegration(unittest.TestCase):
    """Совместная проверка разбора, вычисления и генерации."""

    def test_config_with_constant(self):
        """Константа попадает в XML уже вычисленной."""
        text = '(def PORT 5432); [HOST => "localhost", PORT => ?{PORT}]'
        values = evaluate_tree(parse_config(text), {})
        root = ET.fromstring(generate_xml(values))
        self.assertEqual(root.find("entry/PORT").text, "5432")
        self.assertEqual(root.find("entry/HOST").text, "localhost")

    def test_indented_output(self):
        """Вложенные элементы выводятся на отдельных строках."""
        xml = generate_xml([{"A": 1}])
        expected = (
            "<config>\n"
            "  <entry>\n"
            "    <A>1</A>\n"
            "  </entry>\n"
            "</config>"
        )
        self.assertEqual(xml, expected)

    def test_leaf_text_not_padded(self):
        """Отступы не изменяют текст листовых элементов."""
        root = build_root([{"A": 1}])
        self.assertEqual(root.find("entry/A").text, "1")


if __name__ == "__main__":
    unittest.main()
