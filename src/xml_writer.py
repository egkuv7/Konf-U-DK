"""Модуль для преобразования объектов Python в формат XML."""
import xml.etree.ElementTree as ET


def generate_xml(data):
    """Сгенерировать XML-строку из обработанных данных."""
    root = ET.Element("config")
    for item in data:
        build_element(root, "entry", item)
    return ET.tostring(
        root,
        encoding="unicode",
        method="xml"
    )


def build_element(parent, tag, value):
    """Рекурсивное создание элементов XML."""
    if isinstance(value, dict):
        build_dict_element(parent, tag, value)
    elif isinstance(value, list):
        build_list_element(parent, tag, value)
    else:
        build_primitive_element(parent, tag, value)


def build_dict_element(parent, tag, value):
    """Создать XML-элемент для словаря."""
    elem = ET.SubElement(parent, tag)
    for k, v in value.items():
        build_element(elem, k, v)


def build_list_element(parent, tag, value):
    """Создать XML-элемент для списка."""
    elem = ET.SubElement(parent, tag)
    for item in value:
        build_element(elem, "item", item)


def build_primitive_element(parent, tag, value):
    """Создать XML-элемент для примитивного значения."""
    elem = ET.SubElement(parent, tag)
    elem.text = str(value)
