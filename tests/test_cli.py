"""Интеграционные тесты интерфейса командной строки.

Проверяются ключ -f/--file, вывод XML в стандартный поток вывода,
сообщения об ошибках в стандартный поток ошибок и коды возврата.
"""

import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2


def run_cli(*args):
    """Запустить транслятор отдельным процессом и вернуть результат."""
    command = [sys.executable, "-m", "src.cli", *args]
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        capture_output=True,
        encoding="utf-8",
    )


class TestCli(unittest.TestCase):
    """Тесты поведения инструмента командной строки."""

    def setUp(self):
        """Создать временный каталог для входных файлов."""
        storage = tempfile.TemporaryDirectory()
        self.addCleanup(storage.cleanup)
        self.directory = Path(storage.name)

    def make_file(self, text):
        """Записать конфигурацию во временный файл и вернуть путь."""
        path = self.directory / "input.cfg"
        path.write_text(text, encoding="utf-8")
        return str(path)

    def test_valid_config(self):
        """Корректная конфигурация даёт XML и нулевой код возврата."""
        path = self.make_file("(def N 5); [A => ?{N}]")
        result = run_cli("-f", path)
        self.assertEqual(result.returncode, EXIT_OK)
        self.assertEqual(result.stderr, "")
        root = ET.fromstring(result.stdout)
        self.assertEqual(root.find("entry/A").text, "5")

    def test_long_key(self):
        """Длинный ключ --file равнозначен короткому -f."""
        path = self.make_file("42")
        result = run_cli("--file", path)
        self.assertEqual(result.returncode, EXIT_OK)
        self.assertIn("<config>", result.stdout)

    def test_root_without_declaration(self):
        """Вывод начинается с корня и не содержит декларации XML."""
        path = self.make_file("1")
        result = run_cli("-f", path)
        self.assertTrue(result.stdout.startswith("<config>"))
        self.assertNotIn("<?xml", result.stdout)

    def test_empty_file(self):
        """Пустой файл даёт пустой корневой элемент."""
        path = self.make_file("")
        result = run_cli("-f", path)
        self.assertEqual(result.returncode, EXIT_OK)
        self.assertEqual(result.stdout.strip(), "<config />")

    def test_utf8_values(self):
        """Кириллица проходит через стандартный вывод без потерь."""
        path = self.make_file('[A => "привет"]')
        result = run_cli("-f", path)
        self.assertIn("привет", result.stdout)

    def test_syntax_error(self):
        """Синтаксическая ошибка даёт сообщение и ненулевой код."""
        path = self.make_file('[bg => "#ffffff"]')
        result = run_cli("-f", path)
        self.assertEqual(result.returncode, EXIT_ERROR)
        self.assertEqual(result.stdout, "")
        self.assertIn("Error", result.stderr)

    def test_undefined_constant(self):
        """Необъявленная константа сообщает своё имя в stderr."""
        path = self.make_file("?{MISSING}")
        result = run_cli("-f", path)
        self.assertEqual(result.returncode, EXIT_ERROR)
        self.assertIn("MISSING", result.stderr)

    def test_missing_file(self):
        """Отсутствующий входной файл приводит к ошибке."""
        absent = str(self.directory / "absent.cfg")
        result = run_cli("-f", absent)
        self.assertEqual(result.returncode, EXIT_ERROR)
        self.assertIn("Error", result.stderr)

    def test_missing_key(self):
        """Без ключа -f выводится справка об использовании."""
        result = run_cli()
        self.assertEqual(result.returncode, EXIT_USAGE)
        self.assertIn("usage", result.stderr)

    def test_error_line_number(self):
        """Сообщение об ошибке содержит номер строки входа."""
        path = self.make_file("[A => 1,\n1B => 2]")
        result = run_cli("-f", path)
        self.assertIn("line 2", result.stderr)


if __name__ == "__main__":
    unittest.main()
