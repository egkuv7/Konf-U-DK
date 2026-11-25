"""Модуль для обработки интерфейса командной строки."""
import argparse
import sys
from .parser import parse_config
from .evaluator import evaluate_tree
from .xml_writer import generate_xml


def parse_args():
    """Разбор аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Config language to XML translator."
    )
    parser.add_argument(
        "-f", "--file",
        required=True,
        help="Path to the input configuration file."
    )
    return parser.parse_args()


def main():
    """Основная точка входа для инструмента командной строки."""
    args = parse_args()
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
        
        tree = parse_config(text)
        context = {}
        result = evaluate_tree(tree, context)
        xml_output = generate_xml(result)
        print(xml_output)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
