# Инструмент командной строки для трансляции учебного конфигурационного языка (вариант №15) в формат XML. 
Реализован на Python с использованием специализированного инструмента синтаксического разбора Lark.

## 1. Общее описание

Программа читает файл конфигурации, путь к которому задан ключом `-f`,
выполняет синтаксический анализ, вычисляет константы на этапе трансляции
и печатает XML-документ в стандартный поток вывода. Синтаксические
ошибки и ошибки вычисления выводятся в стандартный поток ошибок.

Синтаксис входного языка:

| Конструкция | Запись |
|---|---|
| Однострочный комментарий | `-- текст` |
| Многострочный комментарий | `#\| текст \|#` |
| Число | `\d+` |
| Строка | `"текст"` |
| Массив | `( значение, значение )` |
| Словарь | `[ ИМЯ => значение ]` |
| Имя | `[_A-Z][_a-zA-Z0-9]*` |
| Объявление константы | `(def ИМЯ значение);` |
| Обращение к константе | `?{ИМЯ}` |

Имя начинается с заглавной латинской буквы или подчёркивания.
Ключом словаря может быть только имя, а не строка: запись
`"bg" => 1` или `bg => 1` является синтаксической ошибкой.

## 2. Функции и настройки

### Ключи командной строки

| Ключ | Назначение |
|---|---|
| `-f`, `--file` | путь к входному файлу конфигурации (обязательный) |
| `-h`, `--help` | справка об использовании |

Коды возврата: `0` — успех, `1` — ошибка разбора, вычисления или
чтения файла, `2` — неверные аргументы командной строки.

### Модули пакета src

- `parser` — `get_parser()`, `parse_config(text)`;
- `evaluator` — `evaluate_tree`, `eval_def`, `eval_expr`,
  `eval_token`, `eval_node`, `resolve_var`, `eval_dict`, `eval_array`;
- `xml_writer` — `generate_xml`, `build_element`,
  `build_dict_element`, `build_list_element`, `build_primitive_element`;
- `cli` — `parse_args()`, `main()`.

### Правила построения XML

- корневой элемент — `config`;
- каждое значение верхнего уровня — элемент `entry`;
- словарь — дочерние элементы с тегами-именами ключей;
- массив — последовательность элементов `item`;
- число или строка — текст элемента;
- символы `&`, `<`, `>` экранируются.

Объявления констант в вывод не попадают: они формируют контекст
вычисления. XML печатается с отступами по два пробела, без
декларации; примеры ниже соответствуют фактическому выводу.

## 3. Сборка и запуск тестов

Требуется Python 3.9+ и библиотека Lark. Все команды выполняются
из корня репозитория.

### Windows, cmd.exe

```bat
chcp 65001
py -3 -m pip install -r requirements.txt
py -3 -m src.cli -f examples\db_config.cfg
py -3 -m unittest discover tests -v
```

```bat
py -3 -X utf8 -m src.cli -f examples\db_config.cfg > out.xml
```

Запуск через скрипт (`run.bat`):
```bat
run.bat
run.bat examples\db_config.cfg
run.bat examples\ui_theme.cfg
run.bat examples\game_stats.cfg
```

Незабуференный вывод при передаче в конвейер:

```bat
py -3 -u -m src.cli -f examples\ui_theme.cfg | more
```

Очистка служебных файлов Python:

```bat
for /d /r %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
del /s /q *.pyc
```

### Linux и macOS, bash

```bash
make install
make run
make test
make clean
```

Без make:

```bash
python3 -m pip install -r requirements.txt
python3 -m src.cli -f examples/db_config.cfg
python3 -m unittest discover tests -v
```

## 4. Примеры использования

### База данных

Вход `examples/db_config.cfg`:

```text
-- Конфигурация подключения к базе данных
(def DB_PORT 5432);
[
    HOST => "localhost",
    PORT => ?{DB_PORT},
    NAME => "production_db",
    POOL => (10, 20, 5)
]
```

Выход:

```xml
<config>
  <entry>
    <HOST>localhost</HOST>
    <PORT>5432</PORT>
    <NAME>production_db</NAME>
    <POOL>
      <item>10</item>
      <item>20</item>
      <item>5</item>
    </POOL>
  </entry>
</config>
```

### Тема интерфейса

Вход `examples/ui_theme.cfg`:

```text
#|
Настройки темы интерфейса:
цвета и размеры шрифтов.
|#
(def PRIMARY_COLOR "blue");
(def FONT_SIZE 14);
[
    THEME => [
        BG => "#ffffff",
        FG => ?{PRIMARY_COLOR},
        SIZES => (12, ?{FONT_SIZE}, 16)
    ]
]
```

Выход:

```xml
<config>
  <entry>
    <THEME>
      <BG>#ffffff</BG>
      <FG>blue</FG>
      <SIZES>
        <item>12</item>
        <item>14</item>
        <item>16</item>
      </SIZES>
    </THEME>
  </entry>
</config>
```

### Персонаж игры

Вход `examples/game_stats.cfg`:

```text
(def BASE_HP 100);
(def LEVEL 5);
[
    CHARACTER => [
        NAME => "Hero",
        HP => ?{BASE_HP},
        LEVEL => ?{LEVEL},
        INVENTORY => ("sword", "shield", "potion")
    ]
]
```

Выход:

```xml
<config>
  <entry>
    <CHARACTER>
      <NAME>Hero</NAME>
      <HP>100</HP>
      <LEVEL>5</LEVEL>
      <INVENTORY>
        <item>sword</item>
        <item>shield</item>
        <item>potion</item>
      </INVENTORY>
    </CHARACTER>
  </entry>
</config>
```

### Сообщения об ошибках

Отсутствующий входной файл:

```bat
py -3 -m src.cli -f bad.cfg
```

```text
Error: [Errno 2] No such file or directory: 'bad.cfg'
```

Синтаксическая ошибка (файл `bad.cfg` содержит `[bg => 1]`):

```bat
py -3 -m src.cli -f bad.cfg
```

```text
Error: No terminal matches 'b' in the current parser context, at line 1 col 2

[bg => 1]
 ^
Expected one of:
        * RSQB
        * NAME
```
-------------------------------------------------
2026
