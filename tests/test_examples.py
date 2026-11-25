"""Сквозные тесты примеров из трёх предметных областей.

Каждый файл каталога examples прогоняется через инструмент командной
строки, результат разбирается как XML и сверяется с ожиданием.
"""

import os
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
EXIT_OK = 0


def translate(name):
    """Прогнать пример через CLI и вернуть разобранный XML-документ."""
    command = [sys.executable, "-m", "src.cli", "-f", str(EXAMPLES / name)]
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        capture_output=True,
        encoding="utf-8",
    )
    if result.returncode != EXIT_OK:
        raise AssertionError(result.stderr)
    return ET.fromstring(result.stdout)


def item_texts(root, path):
    """Собрать тексты элементов, найденных по пути XPath."""
    return [node.text for node in root.findall(path)]


class TestDbConfig(unittest.TestCase):
    """Тесты примера конфигурации базы данных."""

    def test_port_from_constant(self):
        """Порт подставляется из константы DB_PORT."""
        root = translate("db_config.cfg")
        self.assertEqual(root.find("entry/PORT").text, "5432")

    def test_host_and_name(self):
        """Строковые значения словаря переносятся без изменений."""
        root = translate("db_config.cfg")
        self.assertEqual(root.find("entry/HOST").text, "localhost")
        self.assertEqual(root.find("entry/NAME").text, "production_db")

    def test_pool_items(self):
        """Массив пула соединений даёт три элемента item."""
        root = translate("db_config.cfg")
        expected = ["10", "20", "5"]
        self.assertEqual(item_texts(root, "entry/POOL/item"), expected)


class TestUiTheme(unittest.TestCase):
    """Тесты примера конфигурации темы интерфейса."""

    def test_nested_background(self):
        """Вложенный словарь THEME сохраняет значение BG."""
        root = translate("ui_theme.cfg")
        self.assertEqual(root.find("entry/THEME/BG").text, "#ffffff")

    def test_color_constant(self):
        """Цвет подставляется из строковой константы."""
        root = translate("ui_theme.cfg")
        self.assertEqual(root.find("entry/THEME/FG").text, "blue")

    def test_sizes_with_constant(self):
        """Размеры включают константу, вычисленную внутри массива."""
        root = translate("ui_theme.cfg")
        expected = ["12", "14", "16"]
        path = "entry/THEME/SIZES/item"
        self.assertEqual(item_texts(root, path), expected)


class TestGameStats(unittest.TestCase):
    """Тесты примера конфигурации персонажа игры."""

    def test_character_name(self):
        """Имя персонажа переносится во вложенный словарь."""
        root = translate("game_stats.cfg")
        self.assertEqual(root.find("entry/CHARACTER/NAME").text, "Hero")

    def test_hp_and_level(self):
        """Здоровье и уровень подставляются из констант."""
        root = translate("game_stats.cfg")
        self.assertEqual(root.find("entry/CHARACTER/HP").text, "100")
        self.assertEqual(root.find("entry/CHARACTER/LEVEL").text, "5")

    def test_inventory(self):
        """Инвентарь представлен массивом строк."""
        root = translate("game_stats.cfg")
        expected = ["sword", "shield", "potion"]
        path = "entry/CHARACTER/INVENTORY/item"
        self.assertEqual(item_texts(root, path), expected)


class TestAllExamples(unittest.TestCase):
    """Общие проверки набора примеров."""

    def test_single_entry_each(self):
        """Каждый пример описывает одно значение верхнего уровня."""
        for name in ("db_config.cfg", "ui_theme.cfg", "game_stats.cfg"):
            with self.subTest(example=name):
                root = translate(name)
                self.assertEqual([c.tag for c in root], ["entry"])

    def test_examples_present(self):
        """Каталог examples содержит ровно три конфигурации."""
        names = sorted(path.name for path in EXAMPLES.glob("*.cfg"))
        expected = [
            "db_config.cfg",
            "game_stats.cfg",
            "ui_theme.cfg",
        ]
        self.assertEqual(names, expected)


if __name__ == "__main__":
    unittest.main()
