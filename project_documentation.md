# Project Structure: OneFileProject

```
OneFileProject/
├── data/
│   ├── latest_config.json
│   └── version
├── help_texts/
│   ├── en.json
│   └── ru.json
├── installer.py
├── main.py
├── program/
│   ├── commands.py
│   ├── config_utils.py
│   ├── locales/
│   │   ├── en.json
│   │   ├── ru.json
│   │   └── ru.json.new
│   ├── translator.py
│   ├── tui.py
│   └── utils.py
└── requirements.txt
```

# Files Content

## data/latest_config.json

```json
{
  "config_path": "C:\\Users\\anton\\Desktop\\\u041f\u043e\u043b\u0435\u0437\u043d\u044b\u0435 \u0444\u0430\u0439\u043b\u044b\\\u0420\u0430\u0431\u043e\u0442\u0430\\OneFileProject\\project_documenter_config.json",
  "output_path": "C:\\Users\\anton\\Desktop\\\u041f\u043e\u043b\u0435\u0437\u043d\u044b\u0435 \u0444\u0430\u0439\u043b\u044b\\\u0420\u0430\u0431\u043e\u0442\u0430\\OneFileProject\\project_documentation.md",
  "language": "en"
}
```

---


## data/version

```text
v5.1.0
```

---


## help_texts/en.json

```json
{
    "title": "OFP - Project Documentation Generator",
    "usage": "Usage:",
    "commands": "Commands:",
    "options_for_command": "Options:",
    "global_opts": "Global options:",
    "examples": "Examples:",
    "commands_list": [
        ["tui", "Opens the terminal interface"],
        [".", "Document current directory (default)"],
        ["<dir_path>", "Create documentation for specified directory"],
        ["open", "Open output file in default application"],
        ["conf", "Open config file"],
        ["reset", "Reset both config and output files"],
        ["redo", "Regenerate documentation using existing config"],
        ["update", "Update program to latest version"],
        ["unpack", "Unpack project from documentation"],
        ["uninstall", "Uninstall the program"],
        ["help", "Show this help message"],
        ["info", "Show project information"],
        ["pwd", "Show current directory"]
    ],
    "command_options": [
        ["reset", ["-c", "Reset only config file"], ["-o", "Reset only output file"]],
        ["help", ["-ru", "Show help in Russian"], ["-en", "Show help in English"]],
        ["unpack", ["<doc_file>", "Path to the documentation file"], ["<target_dir>", "Path to the target directory"]]
    ],
    "global_options": [
        ["-h, --help", "Show this help message"]
    ],
    "examples_list": [
        ["ofp .", "Document current directory"],
        ["ofp /path/to/project", "Document specified project"],
        ["ofp open", "Open generated documentation"],
        ["ofp reset -c", "Reset only configuration"],
        ["ofp redo", "Regenerate documentation"],
        ["ofp update", "Update program from repository"],
        ["ofp unpack doc.md ./project", "Unpack project from documentation"],
        ["ofp help -ru", "Show help in Russian"]
    ]
}
```

---


## help_texts/ru.json

```json
{
    "title": "OFP - Генератор документации проекта",
    "usage": "Использование:",
    "commands": "Команды:",
    "options_for_command": "Параметры:",
    "global_opts": "Глобальные параметры:",
    "examples": "Примеры:",
    "commands_list": [
        ["tui", "Открывает терминальный интерфейс"],
        [".", "Документировать текущую директорию (по умолчанию)"],
        ["<dir_path>", "Создать документацию для указанной папки"],
        ["open", "Открыть выходной файл в программе по умолчанию"],
        ["conf", "Открыть файл конфигурации"],
        ["reset", "Сбросить и конфиг и выходной файл"],
        ["redo", "Перегенерировать документацию используя существующий конфиг"],
        ["update", "Обновить программу до последней версии"],
        ["unpack", "Распаковать проект из документации"],
        ["uninstall", "Удалить программу"],
        ["help", "Показать эту справку"],
        ["info", "Показать информацию о проекте"],
        ["pwd", "Показать текущую директорию"]
    ],
    "command_options": [
        ["reset", ["-c", "Сбросить только конфигурацию"], ["-o", "Сбросить только выходной файл"]],
        ["help", ["-ru", "Вывести справку на русском"], ["-en", "Вывести справку на английском"]],
        ["unpack", ["<doc_file>", "Путь к файлу документации"], ["<target_dir>", "Путь к целевой директории"]]
    ],
    "global_options": [
        ["-h, --help", "Показать эту справку"]
    ],
    "examples_list": [
        ["ofp .", "Документировать текущую директорию"],
        ["ofp /path/to/project", "Документировать указанный проект"],
        ["ofp open", "Открыть сгенерированную документацию"],
        ["ofp reset -c", "Сбросить только конфигурацию"],
        ["ofp redo", "Перегенерировать документацию"],
        ["ofp update", "Обновить программу из репозитория"],
        ["ofp unpack doc.md ./project", "Распаковать проект из документации"],
        ["ofp help -ru", "Справка на русском языке"]
    ]
}
```

---


## installer.py

```python
import os
import sys
import shutil
import subprocess
import stat
from pathlib import Path


PROGRAM_NAME = "ofp"
PROGRAM_FILES_DIR = "OFP_Documenter"
REPO_URL = "https://github.com/Antongo22/OneFileProject"
DEFAULT_VERSION = "0.0.0"


def handle_remove_readonly(func, path, exc_info):
    """Обработчик для удаления файлов с атрибутом 'только для чтения'"""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def get_install_dir():
    """Возвращает путь для установки программы (без прав админа)"""
    if sys.platform == "win32":
        return Path(os.environ.get('LOCALAPPDATA', 'C:\\Users\\%USERNAME%\\AppData\\Local')) / PROGRAM_FILES_DIR
    else:
        return Path.home() / ".local" / "lib" / PROGRAM_FILES_DIR.lower()


def install_dependencies(install_dir):
    """Устанавливает зависимости из requirements.txt"""
    requirements = install_dir / "requirements.txt"
    if not requirements.exists():
        print("⚠️ requirements.txt not found, skipping dependencies installation")
        return

    print("🔄 Installing dependencies from requirements.txt...")
    try:
        if sys.platform == "win32":
            python_exec = sys.executable
        else:
            python_exec = "python3"

        # Установка базовых зависимостей без импортов
        required_packages = ["colorama", "textual", "typing"]
        print("📦 Installing core dependencies...")
        for pkg in required_packages:
            try:
                subprocess.run(
                    [python_exec, "-m", "pip", "install", pkg],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except Exception as e:
                print(f"⚠️ Warning: Couldn't install {pkg}: {str(e)}")

        # Теперь устанавливаем все остальные зависимости
        subprocess.run(
            [python_exec, "-m", "pip", "install", "-r", str(requirements)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e.stderr.decode().strip()}")
    except Exception as e:
        print(f"❌ Error installing dependencies: {str(e)}")


def get_current_version(install_dir):
    """Получает текущую версию программы без импорта модулей"""
    try:
        version_file = install_dir / "data/version"
        if version_file.exists():
            with open(version_file, 'r') as f:
                return f.read().strip()
    except Exception:
        pass
    return DEFAULT_VERSION


def update():
    """Обновляет программу через git pull с выводом информации о версиях"""
    temp_dir = None
    try:
        install_dir = get_install_dir()
        
        if not install_dir.exists():
            print("❌ Program not installed. Please run installation first.")
            return
            
        current_version = get_current_version(install_dir)

        temp_dir = install_dir.parent / f"{PROGRAM_FILES_DIR}_temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir, onerror=handle_remove_readonly)

        print(f"🔄 Cloning repository for update (current version: {current_version})...")
        subprocess.run(["git", "clone", REPO_URL, temp_dir], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        version_file = temp_dir / "data/version"
        if version_file.exists():
            with open(version_file, 'r') as f:
                new_version = f.read().strip()
        else:
            new_version = "unknown"

        git_dir = temp_dir / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir, onerror=handle_remove_readonly)

        shutil.rmtree(install_dir, onerror=handle_remove_readonly)
        shutil.move(temp_dir, install_dir)

        install_dependencies(install_dir)

        print(f"✅ Successfully updated from version {current_version} to {new_version}!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error when executing git: {e.stderr.decode().strip()}")
    except Exception as e:
        print(f"❌ Update error: {str(e)}")
    finally:
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir, onerror=handle_remove_readonly)
            except Exception:
                pass


def install():
    """Устанавливает программу в пользовательскую директорию"""
    try:
        install_dir = get_install_dir()

        install_dir.mkdir(parents=True, exist_ok=True)
        print(f"🔄 Installing the program in: {install_dir}")

        current_dir = Path(__file__).parent.resolve()
        for item in current_dir.iterdir():
            if item.name not in ['.git', '__pycache__', '.venv', ".idea"]:
                dest = install_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)

        install_dependencies(install_dir)

        if sys.platform == "win32":
            bin_path = Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps"
            bin_path.mkdir(exist_ok=True)
            target_path = bin_path / f"{PROGRAM_NAME}.bat"
            bat_content = f'@python "{install_dir / "main.py"}" %*'
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
        else:
            # Улучшенная установка для Linux
            bin_path = Path.home() / ".local" / "bin"
            bin_path.mkdir(exist_ok=True)
            target_path = bin_path / PROGRAM_NAME

            # Создаем исполняемый файл с улучшенной поддержкой нахождения пути к Python
            with open(target_path, 'w') as f:
                f.write(f"""#!/bin/bash
# Find Python even if the path is not in environment variables
PYTHON_PATH="$(which python3 2>/dev/null || which python 2>/dev/null)"

if [ -z "$PYTHON_PATH" ]; then
    # Check typical Python installation locations
    for path in /usr/bin/python3 /usr/local/bin/python3 /usr/bin/python /usr/local/bin/python; do
        if [ -x "$path" ]; then
            PYTHON_PATH="$path"
            break
        fi
    done

    # If still not found, display error
    if [ -z "$PYTHON_PATH" ]; then
        echo "Error: Python not found. Please install Python 3."
        exit 1
    fi
fi

# Run the program with the found Python
"$PYTHON_PATH" "{install_dir / 'main.py'}" "$@"
""")

            os.chmod(target_path, 0o755)
            
            # Также создаем ссылку в /usr/local/bin, если это возможно (требует sudo)
            try:
                print("\nTrying to create a system link (may require password)...")
                system_bin = Path("/usr/local/bin") / PROGRAM_NAME
                subprocess.run(["sudo", "ln", "-sf", str(target_path), str(system_bin)])
                print(f"✅ System link created: {system_bin}")
            except Exception as e:
                print(f"ℹ️ Could not create system link (this is not an error): {str(e)}")

        print(f"\n✅ The installation is complete! Now use the command '{PROGRAM_NAME}'")

        if sys.platform == "win32":
            print("\n⚠️ For a team to work from anywhere:")
            print(f"1. Press Win+R, type 'sysdm.cpl' and press Enter")
            print("2. Go to the 'Advanced' tab")
            print("3. Click on 'Environment Variables'")
            print(f"4. In the 'System Variables' section, find the 'Path' and click 'Edit'")
            print(f"5. Add a new path: {bin_path}")
        else:
            # Проверяем, добавлен ли путь в PATH
            path_str = os.environ.get('PATH', '')
            if str(bin_path) not in path_str:
                print("\n⚠️ To make the command work from anywhere, add to your ~/.bashrc or ~/.zshrc:")
                print(f'export PATH="$PATH:{bin_path}"')
                print("And run: source ~/.bashrc")
                
                # Автоматически добавляем путь в .bashrc, если файл существует
                bashrc_path = Path.home() / ".bashrc"
                if bashrc_path.exists():
                    try:
                        # Проверяем, не добавлена ли уже эта строка
                        with open(bashrc_path, 'r') as f:
                            content = f.read()
                        
                        if f'export PATH="$PATH:{bin_path}"' not in content:
                            with open(bashrc_path, 'a') as f:
                                f.write(f'\n# Added automatically by {PROGRAM_NAME} installer\nexport PATH="$PATH:{bin_path}"\n')
                            print(f"✅ Path automatically added to {bashrc_path}")
                            print("Run this command to activate changes:")
                            print(f"source {bashrc_path}")
                    except Exception as e:
                        print(f"ℹ️ Failed to automatically update .bashrc: {str(e)}")
                
                # То же самое для .zshrc, если пользователь использует zsh
                zshrc_path = Path.home() / ".zshrc"
                if zshrc_path.exists():
                    try:
                        with open(zshrc_path, 'r') as f:
                            content = f.read()
                        
                        if f'export PATH="$PATH:{bin_path}"' not in content:
                            with open(zshrc_path, 'a') as f:
                                f.write(f'\n# Added automatically by {PROGRAM_NAME} installer\nexport PATH="$PATH:{bin_path}"\n')
                            print(f"✅ Path automatically added to {zshrc_path}")
                            print("Run this command to activate changes:")
                            print(f"source {zshrc_path}")
                    except Exception as e:
                        print(f"ℹ️ Failed to automatically update .zshrc: {str(e)}")

    except Exception as e:
        print(f"\n❌ Installation error: {e}")
        sys.exit(1)





def uninstall():
    """Полностью удаляет программу"""
    try:
        install_dir = get_install_dir()

        if install_dir.exists():
            shutil.rmtree(install_dir)
            print(f"✅ Deleted directory: {install_dir}")

        if sys.platform == "win32":
            target_path = Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps" / f"{PROGRAM_NAME}.bat"
        else:
            target_path = Path.home() / ".local" / "bin" / PROGRAM_NAME

        if target_path.exists():
            target_path.unlink()
            print(f"✅ The command was deleted: {PROGRAM_NAME}")

    except Exception as e:
        print(f"❌ Deletion error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "uninstall":
            uninstall()
        elif sys.argv[1] == "update":
            update()
        else:
            print("❌ Unknown team. Available commands: install, uninstall, update")
    else:
        install()

```

---


## main.py

```python
import os
import sys
from pathlib import Path
from colorama import init
import signal
import program.config_utils as cfg
import installer
import program.utils as utils
import program.commands as commands
from program.tui import run_tui
from program.translator import translator

init(autoreset=True)

translator.set_language(utils.load_latest_config().get('language', 'en'))


def handle_ctrl_c(signum, frame):
    """Обработка нажатия Ctrl+C"""
    print(utils.color_text(f"\n\n{translator.translate('common.canceled')}", 'warning'))
    sys.exit(1)


signal.signal(signal.SIGINT, handle_ctrl_c)



def parse_args():
    """Разбирает аргументы командной строки с проверкой существования папки"""
    lang = utils.load_latest_config().get('language', 'en')
    project_path = None

    if len(sys.argv) > 1:
        if '-ru' in sys.argv:
            lang = 'ru'
            sys.argv.remove('-ru')
        elif '-en' in sys.argv:
            lang = 'en'
            sys.argv.remove('-en')

        translator.set_language(lang)

        if any(x in sys.argv[1:] for x in ("-h", "--help", "help", "помощь")):
            commands.print_help(lang)
            sys.exit(0)
        elif "uninstall" in sys.argv[1:]:
            installer.uninstall()
            sys.exit(0)
        elif "update" in sys.argv[1:]:
            print(utils.color_text(translator.translate('commands.cache_warning'), 'warning'))
            installer.update()
            sys.exit(0)
        elif "open" in sys.argv[1:]:
            commands.open_output_file()
            sys.exit(0)
        elif "conf" in sys.argv[1:]:
            commands.open_config_file()
            sys.exit(0)
        elif "reset" in sys.argv[1:]:
            commands.handle_reset_command()
            sys.exit(0)
        elif "redo" in sys.argv[1:]:
            commands.redo_documentation()
            sys.exit(0)
        elif "version" in sys.argv[1:]:
            version_text = translator.translate('common.version') + ": " + cfg.VERSION
            print(f"{utils.color_text(version_text, 'highlight')}")
            sys.exit(0)
        elif "info" in sys.argv[1:]:
            print(commands.print_project_info())
            sys.exit(0)
        elif "unpack" in sys.argv[1:]:
            if len(sys.argv) < 4:
                print(utils.color_text(translator.translate('commands.unpack_required_args'), 'error'))
                sys.exit(1)
            args = sys.argv[2:]
            doc_file = ' '.join(args[:-1]).strip('"\'')
            target_dir = args[-1].strip('"\'')
            sec, text = commands.unpack(doc_file, target_dir)
            print(text)
            sys.exit(0)
        elif "pwd" in sys.argv[1:]:
            print(utils.color_text(f"{translator.translate('commands.current_working_directory', default='Current working directory')}: {Path(__file__).parent}", 'info'))
            sys.exit(0)
        elif "tree" in sys.argv[1:]:
            # Обрабатываем команду tree
            if len(sys.argv) > 2:
                target_path = sys.argv[2]
            else:
                target_path = os.getcwd()  # Используем текущую директорию если путь не указан
            print(commands.show_directory_tree(target_path))
            sys.exit(0)
        elif "tui" in sys.argv[1:]:
            run_tui()
            sys.exit(0)
        elif "lang" in sys.argv[1:]:
            if len(sys.argv) > 2 and sys.argv[2] in ['en', 'ru']:
                success, message = commands.change_language(sys.argv[2])
                print(utils.color_text(message, 'success' if success else 'error'))
            elif len(sys.argv) == 2:
                # Просто выводим текущий язык без перевода
                if lang == "en":
                    lang_text = "Current language: " + lang
                else:
                    lang_text = "Текущий язык: " + lang
                print(utils.color_text(lang_text, 'info'))
            else:
                print(utils.color_text(translator.translate('commands.usage'), 'error'))
            sys.exit(0)

        if len(sys.argv) > 1 and sys.argv[1] == ".":
            project_path = os.getcwd()
        elif len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            if sys.argv[1] not in ["unpack", "open", "conf", "reset", "redo", "update", "uninstall",
                                   "version", "info", "pwd", "tui", "lang"]:
                potential_path = sys.argv[1]
                if not os.path.exists(potential_path):
                    print(utils.color_text(translator.translate('commands.path_not_exists', path=potential_path), 'error'))
                    sys.exit(1)
                if not os.path.isdir(potential_path):
                    print(utils.color_text(translator.translate('commands.not_directory', path=potential_path), 'error'))
                    sys.exit(1)
                project_path = os.path.abspath(potential_path)

    return project_path






def main():
    cli_project_path = parse_args()
    commands.print_header()

    config = utils.load_config()
    config = utils.edit_config(config, cli_project_path)

    project_path = config.get('project_path', '')
    output_path = config.get('output_path', 'project_documentation.md')

    result = commands.generate_documentation(project_path, output_path, config)
    print(result)

if __name__ == "__main__":
    main()
```

---


## program/commands.py

```python
import program.utils as utils
import os
import sys
import json
import subprocess
from pathlib import Path
import re
import program.config_utils as cfg
from typing import Optional
from program.translator import translator

LANG_PATH = "../help_texts"

def print_help(lang='en'):
    """Выводит информацию о доступных командах и флагах из JSON-файлов"""
    try:
        help_file = Path(__file__).parent / LANG_PATH / f'{lang}.json'
        if not help_file.exists():
            help_file = Path(__file__).parent / LANG_PATH / 'en.json'
        with open(help_file, 'r', encoding='utf-8') as f:
            texts = json.load(f)
        help_text = f"""
{utils.color_text(texts['title'], 'highlight')}
{utils.color_text(texts['usage'], 'info')}
    {cfg.PROGRAM_NAME} [command] [options]
{utils.color_text(texts['commands'], 'info')}"""

        # Создаем словарь флагов для каждой команды
        command_flags = {}
        for cmd_info in texts.get('command_options', []):
            if len(cmd_info) >= 2:
                cmd_name = cmd_info[0]
                flags = cmd_info[1:]
                command_flags[cmd_name] = flags
                
        # Выводим команды и их флаги
        for cmd_info in texts['commands_list']:
            cmd, desc = cmd_info
            max_pad = 20
            cmd_pad = max(max_pad - len(cmd), 1)
            help_text += f"\n    {utils.color_text(cmd, 'path')}{' ' * cmd_pad}{desc}"
            
            # Добавляем флаги для этой команды, если они есть
            if cmd in command_flags and command_flags[cmd]:
                help_text += f"\n      {utils.color_text(texts.get('options_for_command', 'Options:'), 'info')}"
                for flag_info in command_flags[cmd]:
                    if len(flag_info) >= 2:
                        flag, flag_desc = flag_info
                        flag_pad = max(max_pad - len(flag) - 4, 1)
                        help_text += f"\n        {utils.color_text(flag, 'path')}{' ' * flag_pad}{flag_desc}"

        # Добавляем общие флаги, если они есть
        if 'global_options' in texts and texts['global_options']:
            help_text += f"\n\n{utils.color_text(texts.get('global_opts', 'Global options:'), 'info')}"
            for opt, desc in texts['global_options']:
                opt_pad = max(max_pad - len(opt), 1)
                help_text += f"\n    {utils.color_text(opt, 'path')}{' ' * opt_pad}{desc}"
            
        help_text += f"\n\n{utils.color_text(texts['examples'], 'info')}"
        for ex, desc in texts['examples_list']:
            ex_pad = max(30 - len(ex), 1)
            help_text += f"\n    {utils.color_text(ex, 'highlight')}{' ' * ex_pad}{desc}"
            
        print(f"\n{help_text}\n")
    except Exception as e:
        print(utils.color_text(f"\n{translator.translate('commands.loading_help_error', error=str(e))}\n", 'error'))


def print_project_info() -> str:
    """Выводит информацию о проекте с цветным оформлением"""
    # Получаем переводы заранее, чтобы избежать проблем с отображением ключей
    info_title = translator.translate("common.information")
    author_title = translator.translate("common.author")
    repo_title = translator.translate("common.repository")
    version_title = translator.translate("common.version")
    
    return f"""
{utils.color_text(info_title, 'info')}
{utils.color_text(author_title, 'info')} {utils.color_text("Anton Aleynichenko - https://aleynichenko.ru", 'highlight')}
{utils.color_text(repo_title, 'info')} {utils.color_text("https://github.com/Antongo22/OneFileProject", 'highlight')}
{utils.color_text(version_title, 'info')} {utils.color_text(cfg.VERSION, 'highlight')}
"""


def unpack(doc_file: str, target_dir: str) -> (bool, Optional[str]):
    """Распаковывает проект из файла документации"""

    res = ""
    try:
        doc_path = Path(doc_file.strip('"\''))
        target_path = Path(target_dir.strip('"\''))

        if not doc_path.exists():
            return False, utils.color_text(translator.translate("commands.file_not_found", path=doc_path), 'error')

        if target_path.exists() and any(target_path.iterdir()):
            return False, utils.color_text(translator.translate("commands.target_not_empty", path=target_path), 'error')

        target_path.mkdir(parents=True, exist_ok=True)

        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        structure_match = re.search(
            r'# (?:Структура проекта|Project Structure):.*?\n```.*?\n(.*?)\n```',
            content,
            re.DOTALL
        )

        if not structure_match:
            return False, utils.color_text(translator.translate("commands.doc_section_not_found"), 'error')

        first_line = structure_match.group(1).split('\n')[0].strip()
        root_folder_name = first_line.split('/')[0].rstrip('\\/')

        files_section = re.finditer(
            r'## (.*?)\n```(?:.*?)\n(.*?)\n```\n(?:---)?',
            content,
            re.DOTALL
        )

        for match in files_section:
            rel_path = match.group(1).strip()
            file_content = match.group(2).strip()

            if rel_path.startswith(root_folder_name + '/'):
                rel_path = rel_path[len(root_folder_name) + 1:]

            rel_path = rel_path.replace('│', '').strip()

            try:
                file_path = target_path / rel_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
            except Exception as e:
                 res += utils.color_text(translator.translate("commands.file_creation_error", file=rel_path, error=str(e)), 'warning') + "\n"

        res += utils.color_text(translator.translate("commands.unpack_success", path=target_path), 'success') + "\n"
        return True, res
    except Exception as e:
        res += utils.color_text(translator.translate("commands.unpack_error", error=str(e)), 'error')
        return False, res


def open_output_file(isOpen: bool = True) -> Optional[Path]:
    """Открывает выходной файл в приложении по умолчанию"""
    config = utils.load_config()
    output_path = None

    if config.get('output_path'):
        output_path = Path(config['output_path'])
        if not output_path.exists():
            output_path = None

    if output_path is None:
        latest_paths = utils.load_latest_paths()
        if latest_paths.get('output_path'):
            output_path = Path(latest_paths['output_path'])
            if not output_path.exists():
                output_path = None

    if output_path is None:
        print(utils.color_text("Error: Output file not found in config or latest paths", 'error'))
        return None

    if not isOpen:
        return output_path

    try:
        if sys.platform == 'win32':
            os.startfile(output_path)
        elif sys.platform == 'darwin':
            subprocess.run(['open', output_path])
        else:
            subprocess.run(['xdg-open', output_path])
        print(utils.color_text(f"Opened output file: {output_path}", 'success'))
        return output_path
    except Exception as e:
        print(utils.color_text(f"Error opening file: {str(e)}", 'error'))
        return None


def open_config_file() -> Optional[Path]:
    """Открывает файл конфигурации в приложении по умолчанию"""
    config_path = utils.get_config_path()
    if not config_path.exists():
        latest_paths = utils.load_latest_paths()
        if latest_paths.get('config_path'):
            config_path = Path(latest_paths['config_path'])
            if not config_path.exists():
                print(utils.color_text("Error: Config file not found in standard or latest paths", 'error'))
                return None

    try:
        if sys.platform == 'win32':
            os.startfile(config_path)
        elif sys.platform == 'darwin':
            subprocess.run(['open', config_path])
        else:
            subprocess.run(['xdg-open', config_path])
        print(utils.color_text(f"Opened config file: {config_path}", 'success'))
        return config_path
    except Exception as e:
        print(utils.color_text(f"Error opening config file: {str(e)}", 'error'))
        return None


def handle_reset_command():
    """Обрабатывает команду reset"""
    if len(sys.argv) > 2:
        if sys.argv[2] == '-c':
            reset_config()
        elif sys.argv[2] == '-o':
            reset_output()
        else:
            print(utils.color_text("Invalid reset option. Use -c for config or -o for output", 'error'))
    else:
        reset_config()
        reset_output()


def reset_config():
    """Сбрасывает конфигурацию"""
    try:
        config_path = utils.get_config_path()
        if config_path.exists():
            config_path.unlink()
            print(utils.color_text("Config file has been reset", 'success'))
        else:
            print(utils.color_text("Config file does not exist", 'warning'))
    except Exception as e:
        print(utils.color_text(f"Error resetting config: {str(e)}", 'error'))


def reset_output():
    """Сбрасывает выходной файл"""
    config = utils.load_config()
    if not config['output_path']:
        print(utils.color_text("Output path is not set in config", 'warning'))
        return

    output_path = Path(config['output_path'])
    try:
        if output_path.exists():
            output_path.unlink()
            print(utils.color_text(f"Output file {output_path} has been reset", 'success'))
        else:
            print(utils.color_text(f"Output file {output_path} does not exist", 'warning'))
    except Exception as e:
        print(utils.color_text(f"Error resetting output file: {str(e)}", 'error'))


def redo_documentation():
    """Повторно генерирует документацию с проверкой latest_paths.json"""
    config_path = utils.get_config_path()
    config = None

    if config_path.exists():
        try:
            config = utils.load_config()
        except Exception as e:
            print(utils.color_text(f"Error loading config: {str(e)}", 'error'))

    if config is None:
        latest_paths = utils.load_latest_paths()
        if latest_paths.get('config_path'):
            alt_config_path = Path(latest_paths['config_path'])
            if alt_config_path.exists() and alt_config_path != config_path:
                print(utils.color_text(f"Trying config from latest paths: {alt_config_path}", 'info'))
                try:
                    config = utils.load_config()
                    config_path = alt_config_path
                except Exception as e:
                    print(utils.color_text(f"Error loading config from latest paths: {str(e)}", 'error'))

    if config is None:
        print(utils.color_text("Error: No valid config file found", 'error'))
        return

    if not config.get('project_path'):
        config['project_path'] = str(config_path.parent)
        print(utils.color_text(f"Using parent directory of config file as project path: {config['project_path']}", 'info'))

    try:
        root_path = os.path.normpath(config['project_path'])
        root_name = os.path.basename(root_path)

        print(utils.color_text("\nScanning project structure...", 'info'))
        print(utils.color_text("\nScanning project structure...", 'info'))
        tree, files = utils.generate_file_tree(root_path, config)

        print(utils.color_text("\nGenerating documentation...", 'info'))
        md_content = (
            f"# Project Structure: {root_name}\n\n"
            f"```\n{root_name}/\n{tree}\n```\n\n"
            f"# Files Content\n\n{utils.get_file_contents(files)}"
        )

        output_path = Path(config['output_path'])
        if not output_path.parent.exists():
            latest_paths = utils.load_latest_paths()
            if latest_paths.get('output_path'):
                output_path = Path(latest_paths['output_path'])
                print(utils.color_text(f"Using output path from latest paths: {output_path}", 'info'))

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)


        print(utils.color_text("\nDocumentation regenerated successfully!", 'success'))
        print(utils.color_text(f"Output file: {output_path}", 'path'))
        print(utils.color_text(f"Total files processed: {len(files)}", 'info'))

    except Exception as e:
        print(utils.color_text(f"\nError: {str(e)}", 'error'))




def print_header():
    """Выводит цветной заголовок программы"""
    header = f"""
   ____               ______ _ _        _____           _           _   
  / __ \             |  ____(_) |      |  __ \         (_)         | |  
 | |  | |_ __   ___  | |__   _| | ___  | |__) | __ ___  _  ___  ___| |_ 
 | |  | | '_ \ / _ \ |  __| | | |/ _ \ |  ___/ '__/ _ \| |/ _ \/ __| __|
 | |__| | | | |  __/ | |    | | |  __/ | |   | | | (_) | |  __/ (__| |_ 
  \____/|_| |_|\___| |_|    |_|_|\___| |_|   |_|  \___/| |\___|\___|\__|
                                                      _/ |              
                                                     |__/              
    {cfg.PROGRAM_NAME.upper()} {cfg.VERSION}
    """
    # Заголовок не переводим, так как это ASCII-арт
    print(utils.color_text(header, 'highlight'))
    print(utils.color_text("=" * 60, 'info') + "\n")
def generate_documentation(project_path: str, output_path: str, config: Optional[dict] = None) -> str:
    """
    Генерирует документацию проекта и сохраняет в указанный файл
    Возвращает строку с результатом операции
    """
    from pathlib import Path
    import os
    from program import utils

    if config is None:
        config = utils.load_config()

    if not project_path:
        return utils.color_text(translator.translate("commands.project_required"), 'error')

    if not os.path.isdir(project_path):
        return utils.color_text(translator.translate("commands.dir_not_exists", path=project_path), 'error')

    try:
        root_path = os.path.normpath(project_path)
        root_name = os.path.basename(root_path)

        config['project_path'] = project_path
        config['output_path'] = output_path

        tree, files = utils.generate_file_tree(root_path, config)

        # Получаем заголовки из переводчика
        structure_title = translator.translate('doc.structure_title')
        files_content_title = translator.translate('doc.files_content_title')

        md_content = (
            f"# {structure_title}: {root_name}\n\n"
            f"```\n{root_name}/\n{tree}\n```\n\n"
            f"# {files_content_title}\n\n{utils.get_file_contents(files)}"
        )

        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path_obj, 'w', encoding='utf-8') as f:
            f.write(md_content)

        utils.save_config(config)
        utils.save_latest_paths(str(output_path_obj), utils.load_latest_config())

        result = (
            f"{utils.color_text(translator.translate('commands.doc_generated'), 'success')}\n"
            f"{utils.color_text(translator.translate('commands.output_file', path=output_path), 'path')}\n"
            f"{utils.color_text(translator.translate('commands.files_processed', count=len(files)), 'info')}"
        )
        return result

    except Exception as e:
        return utils.color_text(f"\n{translator.translate('common.error')}: {str(e)}", 'error')


def ansi_to_textual(text: str) -> str:
    """Конвертирует ANSI-цвета в Textual-разметку"""
    color_map = {
        '\x1b[31m': '[red]',
        '\x1b[32m': '[green]',
        '\x1b[33m': '[yellow]',
        '\x1b[34m': '[blue]',
        '\x1b[35m': '[magenta]',
        '\x1b[36m': '[cyan]',
        '\x1b[0m': '[/]',
        '\x1b[1m': '[b]',
        '\x1b[4m': '[u]'
    }
    for ansi, textual in color_map.items():
        text = text.replace(ansi, textual)
    return text


def change_language(lang: str):
    """Меняет язык интерфейса"""
    if lang not in ['en', 'ru']:
        return False, translator.translate("commands.invalid_language")

    try:
        latest_config = utils.load_latest_config()
        latest_config['language'] = lang
        with open(cfg.LATEST_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(latest_config, f, indent=2)
        translator.set_language(lang)  # Устанавливаем язык сразу после смены
        return True, translator.translate("commands.language_changed", lang=lang)
    except Exception as e:
        return False, translator.translate("commands.language_change_error", error=str(e))


def show_directory_tree(directory_path: str) -> str:
    """Отображает древовидную структуру директории в консоли"""
    print(utils.color_text(f"Generating directory tree for: {directory_path}", 'info'))
    try:
        if not os.path.exists(directory_path):
            return utils.color_text(translator.translate("commands.path_not_exists", path=directory_path), 'error')
        if not os.path.isdir(directory_path):
            return utils.color_text(translator.translate("commands.not_directory", path=directory_path), 'error')
            
        directory_path = os.path.abspath(directory_path)
        root_name = os.path.basename(directory_path)
        
        # Создадим минимальную конфигурацию для отображения структуры
        config = {
            'ignore_folders': ['.git', '__pycache__', '.venv', 'node_modules'],
            'ignore_files': ['*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.exe'],
            'ignore_paths': [],
            'show_hidden': False,
            'whitelist_paths': []
        }
        
        # Загружаем пользовательскую конфигурацию и мержим с базовой
        user_config = utils.load_config()
        if user_config:
            for key in ['ignore_folders', 'ignore_files', 'ignore_paths', 'show_hidden', 'whitelist_paths']:
                if key in user_config:
                    config[key] = user_config[key]
        
        # Создаем дерево директорий с помощью собственной функции
        def build_tree(path, prefix=''):
            files = []
            dirs = []
            
            # Сортируем содержимое по директориям и файлам
            try:
                for item in sorted(os.listdir(path)):
                    full_path = os.path.join(path, item)
                    rel_path = os.path.relpath(full_path, directory_path)
                    
                    # Проверяем следует ли пропустить путь
                    if not config['show_hidden'] and item.startswith('.'):
                        continue
                    if any(re.match(pattern.replace('*', '.*'), item) for pattern in config['ignore_files']) and not os.path.isdir(full_path):
                        continue
                    if item in config['ignore_folders'] and os.path.isdir(full_path):
                        continue
                    if any(re.match(pattern.replace('*', '.*'), rel_path) for pattern in config['ignore_paths']):
                        continue
                    
                    if config['whitelist_paths'] and not any(re.match(pattern.replace('*', '.*'), rel_path) for pattern in config['whitelist_paths']):
                        if not any(rel_path.startswith(os.path.normpath(p)) for p in config['whitelist_paths']):
                            continue
                            
                    if os.path.isdir(full_path):
                        dirs.append(item)
                    else:
                        files.append(item)
            except PermissionError:
                return "├── [Permission denied]\n"
            except Exception as e:
                return f"├── [Error: {str(e)}]\n"
            
            tree = ""
            count = len(dirs) + len(files)
            idx = 0
            
            # Сначала выводим директории
            for i, d in enumerate(dirs):
                idx += 1
                is_last = (idx == count)
                current_prefix = "└── " if is_last else "├── "
                next_prefix = "    " if is_last else "│   "
                full_path = os.path.join(path, d)
                tree += f"{prefix}{current_prefix}{d}/\n"
                tree += build_tree(full_path, prefix + next_prefix)
            
            # Затем файлы
            for i, f in enumerate(files):
                idx += 1
                is_last = (idx == count)
                tree += f"{prefix}{'└── ' if is_last else '├── '}{f}\n"
            
            return tree
        
        # Строим дерево
        tree = build_tree(directory_path)
        result = f"\n{root_name}/\n{tree}"
        return utils.color_text(result, 'highlight')
    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        return utils.color_text(f"\n{translator.translate('common.error')}: {str(e)}\n{trace}", 'error')

```

---


## program/config_utils.py

```python
from pathlib import Path
from colorama import Fore

PREFIX = "../data"
VERSION_FILE=f'{PREFIX}/version'

PROGRAM_NAME = "ofp"
CONFIG_FILE = "project_documenter_config.json"
LATEST_CONFIG_FILE = str(Path(__file__).parent / f"{PREFIX}/latest_config.json")


def get_version():
    """Получает версию из файла version или возвращает v0.0.0 при ошибке"""
    try:
        with open(Path(__file__).parent / VERSION_FILE  , 'r') as f:
            version = f.read().strip()
            if version and version[0].isdigit():
                return f"v{version.split()[0]}"
            return version.split()[0] if version else "v/././"
    except:
        return "v0.0.0"


VERSION = get_version()

COLORS = {
    'error': Fore.RED,
    'success': Fore.GREEN,
    'warning': Fore.YELLOW,
    'info': Fore.CYAN,
    'path': Fore.BLUE,
    'highlight': Fore.MAGENTA
}

LANGUAGE_MAPPING = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.java': 'java',
    '.kt': 'kotlin',
    '.cpp': 'cpp',
    '.h': 'c',
    '.c': 'c',
    '.cs': 'csharp',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.html': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.less': 'less',
    '.json': 'json',
    '.xml': 'xml',
    '.yml': 'yaml',
    '.yaml': 'yaml',
    '.toml': 'toml',
    '.ini': 'ini',
    '.conf': 'ini',
    '.env': 'ini',
    '.sh': 'bash',
    '.bash': 'bash',
    '.zsh': 'bash',
    '.fish': 'bash',
    '.ps1': 'powershell',
    '.csv': 'csv',
    '.tsv': 'csv',
    '.sql': 'sql',
    '.md': 'markdown',
    '.txt': 'text',
}

DEFAULT_CONFIG = {
    'project_path': '',
    'output_path': 'project_documentation.md',
    'ignore_folders': ['.git', '__pycache__', '.venv'],
    'ignore_files': [
        '.gitignore', '.env', CONFIG_FILE, 'latest_paths.json', '*.md',
        '*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.tiff', '*.svg',
        '*.mp3', '*.mp4', '*.avi', '*.mov', '*.wav',
        '*.zip', '*.tar', '*.gz', '*.rar', '*.7z',
        '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx', '*.ppt', '*.pptx',
        '*.exe', '*.dll', '*.so', '*.bin',
        '*.iml', '*.swp', '*.swo',
        '*.ico', '*.icns', '*.jar', '*.war'
    ],
    'ignore_paths': [],
    'whitelist_paths': [],
    'show_hidden': False
}

DEFAULT_LATEST_CONFIG = {
    'language': 'en'
}
```

---


## program/locales/en.json

```json
{
    "common": {
        "header_title": "OneFileProject TUI",
        "error": "Error",
        "success": "Success",
        "warning": "Warning",
        "info": "Info",
        "canceled": "Operation canceled by user",
        "version": "Version",
        "author": "Author",
        "author_name": "Anton Aleynichenko - https://aleynichenko.ru",
        "repository": "Repository",
        "repository_url": "https://github.com/Antongo22/OneFileProject",
        "information": "Project Information",
        "confirm": "Confirm",
        "cancel": "Cancel",
        "save": "Save",
        "path": "Path",
        "directory": "Directory",
        "file": "File"
    },
    "commands": {
        "error_loading_help": "Error loading help: {error}",
        "file_not_found": "File not found: {path}",
        "target_not_empty": "Target directory is not empty: {path}",
        "doc_section_not_found": "Required documentation section not found",
        "file_create_error": "Error creating file: {error}",
        "unpack_success": "Project successfully unpacked to {path}",
        "output_file_not_found": "Error: Output file not found in config or latest paths",
        "opened_output_file": "Opened output file: {path}",
        "error_opening_file": "Error opening file: {error}",
        "config_file_not_found": "Error: Config file not found in standard or latest paths",
        "opened_config_file": "Opened config file: {path}",
        "error_opening_config": "Error opening config file: {error}",
        "invalid_reset_option": "Invalid reset option. Use -c for config or -o for output",
        "config_reset": "Config file has been reset",
        "config_not_exist": "Config file does not exist",
        "error_resetting_config": "Error resetting config: {error}",
        "output_not_set": "Output path is not set in config",
        "output_reset": "Output file {path} has been reset",
        "output_not_exist": "Output file {path} does not exist",
        "error_resetting_output": "Error resetting output file: {error}",
        "error_loading_config_redo": "Error loading config: {error}",
        "config_from_latest": "Trying config from latest paths: {path}",
        "latest_path_error": "Error loading config from latest paths: {error}",
        "no_valid_config": "Error: No valid config file found",
        "using_parent_dir": "Using parent directory of config file as project path: {path}",
        "scanning_project": "\nScanning project structure...",
        "generating_doc": "\nGenerating documentation...",
        "output_from_latest": "Using output path from latest paths: {path}",
        "doc_regenerated": "\nDocumentation regenerated successfully!",
        "output_file": "Output file: {path}",
        "files_processed": "Total files processed: {count}",
        "error_generate": "\nError: {error}",
        "project_required": "Project path is required",
        "dir_not_exists": "Directory does not exist: {path}",
        "doc_generated": "Documentation successfully generated!",
        "invalid_language": "Invalid language. Use 'en' or 'ru'",
        "language_changed": "Language changed to {lang}",
        "language_change_error": "Error changing language: {error}",
        "cache_warning": "This will clear cache files. Continue? (y/n) [n]",
        "current_language": "Current language: {lang}",
        "usage": "Usage: ofp lang [en|ru]",
        "current_working_directory": "Current working directory",
        "unpack_required_args": "Error: unpack requires 2 arguments - the documentation file and the target folder",
        "path_not_exists": "Error: Path '{path}' does not exist!",
        "not_directory": "Error: '{path}' is not a directory!",
        "loading_help_error": "Error loading help: {error}",
        "config_reset": "Config file has been reset",
        "config_not_exists": "Config file does not exist",
        "reset_config_error": "Error resetting config: {error}",
        "output_reset": "Output file {path} has been reset",
        "output_not_exists": "Output file {path} does not exist",
        "reset_output_error": "Error resetting output file: {error}",
        "output_path_not_set": "Output path is not set in config",
        "invalid_reset_option": "Invalid reset option. Use -c for config or -o for output",
        "output_not_found": "Error: Output file not found in config or latest paths",
        "opened_output": "Opened output file: {path}",
        "open_file_error": "Error opening file: {error}",
        "config_not_found": "Error: Config file not found in standard or latest paths",
        "opened_config": "Opened config file: {path}",
        "open_config_error": "Error opening config file: {error}",
        "loading_config_error": "Error loading config: {error}",
        "saving_config_error": "Error saving config: {error}",
        "config_saved": "Configuration saved successfully in {path}",
        "no_project_path": "Cannot save config: project path is not set",
        "no_valid_config": "Error: No valid config file found",
        "using_parent_dir": "Using parent directory of config file as project path: {path}",
        "latest_paths_config": "Using output path from latest paths: {path}",
        "file_creation_error": "Failed to create {file} file: {error}",
        "unpack_success": "The project has been successfully unpacked in: {path}",
        "unpack_error": "Unpacking error: {error}",
        "doc_section_not_found": "Error: The section with the project structure was not found.",
        "file_not_found": "Error: The documentation file '{path}' was not found",
        "target_not_empty": "Error: The target directory '{path}' is not empty",
        "project_required": "Error: Project path is required!",
        "dir_not_exists": "Error: Directory '{path}' does not exist!",
        "doc_generated": "Documentation generated successfully!",
        "output_file": "Output file: {path}",
        "files_processed": "Total files processed: {count}",
        "scanning_structure": "Scanning project structure...",
        "generating_docs": "Generating documentation...",
        "doc_regenerated": "Documentation regenerated successfully!",
        "cache_warning": "The entire cache will be cleared!",
        "uninstall_deleted_dir": "Deleted directory: {path}",
        "uninstall_deleted_cmd": "The command was deleted: {cmd}",
        "uninstall_error": "Deletion error: {error}",
        "unknown_command": "Unknown team. Available commands: install, uninstall, update",
        "path_instructions_win": "For a team to work from anywhere:\n1. Press Win+R, type 'sysdm.cpl' and press Enter\n2. Go to the 'Advanced' tab\n3. Click on 'Environment Variables'\n4. In the 'System Variables' section, find the 'Path' and click 'Edit'\n5. Add a new path: {path}",
        "path_instructions_linux": "Add it to ~/.bashrc or ~/.zshrc:\nexport PATH=\"$PATH:{path}\"\nAnd run: source ~/.bashrc"
    },
    "installer": {
        "install_start": "Installing the program in: {path}",
        "install_complete": "The installation is complete! Now use the command '{cmd}'",
        "install_error": "Installation error: {error}",
        "deps_install": "Installing dependencies from requirements.txt...",
        "deps_installed": "Dependencies installed successfully",
        "deps_install_error": "Failed to install dependencies: {error}",
        "deps_install_unknown": "Error installing dependencies: {error}",
        "requirements_not_found": "requirements.txt not found, skipping dependencies installation",
        "update_start": "Cloning the repository for updating (current version: {version})...",
        "update_complete": "The program has been successfully updated from {old_version} to {new_version}!",
        "update_error": "Update error: {error}",
        "git_error": "Error when executing git: {error}",
        "not_installed": "The program is not installed. First, perform the installation.",
        "uninstall_deleted_dir": "Deleted directory: {path}",
        "uninstall_deleted_cmd": "The command was deleted: {cmd}",
        "uninstall_error": "Deletion error: {error}",
        "unknown_command": "Unknown team. Available commands: install, uninstall, update",
        "path_instructions_win": "For a team to work from anywhere:\n1. Press Win+R, type 'sysdm.cpl' and press Enter\n2. Go to the 'Advanced' tab\n3. Click on 'Environment Variables'\n4. In the 'System Variables' section, find the 'Path' and click 'Edit'\n5. Add a new path: {path}",
        "path_instructions_linux": "Add it to ~/.bashrc or ~/.zshrc:\nexport PATH=\"$PATH:{path}\"\nAnd run: source ~/.bashrc"
    },
    "tui": {
        "config_saved": "Configuration saved!",
        "json_error": "JSON error: {error}",
        "generation_preparing": "Preparing for generation...",
        "generation_canceled": "Canceled",
        "generation_started": "Documentation generation in progress...",
        "generation_complete": "Generation complete!\n{result}",
        "generation_error": "Generation error: {error}",
        "opening_doc": "Opening documentation...",
        "doc_not_found_red": "Documentation not found!",
        "doc_opened_green": "Documentation opened:\n{path}",
        "open_error_red": "Error: {error}",
        "opening_config": "Trying to open config...",
        "config_not_found_red": "Config not found!",
        "config_opened_green": "Config opened in {path}",
        "config_error_red": "Error: {error}",
        "info_error": "Error loading info",
        "unpack_paths_required": "Specify both paths!",
        "unpack_error_red": "Error: {error}",
        "app_title": "One File Project",
        "generate_button": "Generate Documentation",
        "open_docs_button": "Open Documentation",
        "config_button": "Config",
        "edit_config_button": "Edit Config",
        "unpack_button": "Unpack Project",
        "info_button": "Info",
        "view_md_button": "View Markdown",
        "language_button": "Change Language",
        "choose_language": "Choose language:",
        "footer_highlight_key": "KEY",
        "doc_file_label": "Documentation file path:",
        "target_dir_label": "Target directory path:",
        "unpack_button_confirm": "Unpack",
        "enter_path": "Enter path or leave current",
        "path_input_title": "Enter path:",
        "confirm_path": "Confirm Path",
        "close": "Close",
        "project_path_title": "Project path:",
        "output_path_title": "Output path:"
    },
    "utils": {
        "error_saving_latest_config": "Error saving latest config: {error}",
        "error_loading_latest_config": "Error loading latest config: {error}",
        "error_loading_latest_paths": "Error loading latest paths: {error}",
        "error_loading_config": "Error loading config: {error}",
        "cannot_save_config": "Cannot save config: project path is not set",
        "config_saved_successfully": "Configuration saved successfully in {path}",
        "error_saving_config": "Error saving config: {error}",
        "current_configuration": "Current configuration:",
        "edit_configuration": "Edit configuration:",
        "filter_settings": "Filter settings:",
        "whitelist_settings": "Whitelist settings:",
        "current_whitelist_paths": "Current whitelist paths (empty means all files):",
        "ignore_settings": "Ignore settings:",
        "current_ignored_folders": "Current ignored folders:",
        "current_ignored_files": "Current ignored files:",
        "current_ignored_paths": "Current ignored paths:",
        "project_path": "Project path",
        "output_file_path": "Output file path",
        "show_hidden_files": "Show hidden files? (y/n) [n]:",
        "edit_question": "Edit? (y/n) [n]:",
        "enter_paths_to_include": "Enter paths to include (comma separated, * for wildcard, relative to project):",
        "enter_folders_to_ignore": "Enter folders to ignore (comma separated):",
        "enter_file_patterns_to_ignore": "Enter file patterns to ignore (comma separated, * for wildcard):",
        "enter_full_paths_to_ignore": "Enter full paths to ignore (comma separated, * for wildcard):"
    },
    "ui": {
        "header_title": "ONE FILE PROJECT DOCUMENTATION",
        "footer_help": "Help: Press ? for more information"
    },
    "doc": {
        "structure_title": "Project Structure",
        "files_content_title": "Files Content"
    }
}
```

---


## program/locales/ru.json

```json
{
    "common": {
        "header_title": "OneFileProject TUI",
        "error": "Ошибка",
        "success": "Успех",
        "warning": "Предупреждение",
        "info": "Информация",
        "canceled": "Операция отменена пользователем",
        "version": "Версия",
        "author": "Автор",
        "author_name": "Антон Алейниченко - https://aleynichenko.ru",
        "repository": "Репозиторий",
        "repository_url": "https://github.com/Antongo22/OneFileProject",
        "information": "Общая информация",
        "confirm": "Подтвердить",
        "cancel": "Отмена",
        "save": "Сохранить",
        "path": "Путь",
        "directory": "Директория",
        "file": "Файл"
    },
    "commands": {
        "error_loading_help": "Ошибка загрузки справки: {error}",
        "file_not_found": "Файл не найден: {path}",
        "target_not_empty": "Целевая директория не пуста: {path}",
        "doc_section_not_found": "Необходимая секция документации не найдена",
        "file_create_error": "Ошибка создания файла: {error}",
        "unpack_success": "Проект успешно распакован в {path}",
        "output_file_not_found": "Ошибка: Выходной файл не найден в конфигурации или последних путях",
        "opened_output_file": "Открыт выходной файл: {path}",
        "error_opening_file": "Ошибка открытия файла: {error}",
        "config_file_not_found": "Ошибка: Файл конфигурации не найден в стандартных или последних путях",
        "opened_config_file": "Открыт файл конфигурации: {path}",
        "error_opening_config": "Ошибка открытия файла конфигурации: {error}",
        "invalid_reset_option": "Неверная опция сброса. Используйте -c для конфигурации или -o для выходного файла",
        "config_reset": "Файл конфигурации был сброшен",
        "config_not_exist": "Файл конфигурации не существует",
        "error_resetting_config": "Ошибка сброса конфигурации: {error}",
        "output_not_set": "Выходной путь не задан в конфигурации",
        "output_reset": "Выходной файл {path} был сброшен",
        "output_not_exist": "Выходной файл {path} не существует",
        "error_resetting_output": "Ошибка сброса выходного файла: {error}",
        "error_loading_config_redo": "Ошибка загрузки конфигурации: {error}",
        "config_from_latest": "Пробую конфигурацию из последних путей: {path}",
        "latest_path_error": "Ошибка загрузки конфигурации из последних путей: {error}",
        "no_valid_config": "Ошибка: Не найдено действительного файла конфигурации",
        "using_parent_dir": "Использую родительскую директорию файла конфигурации как путь к проекту: {path}",
        "scanning_project": "\nСканирование структуры проекта...",
        "generating_doc": "\nГенерация документации...",
        "output_from_latest": "Использую выходной путь из последних путей: {path}",
        "doc_regenerated": "\nДокументация успешно перегенерирована!",
        "output_file": "Выходной файл: {path}",
        "files_processed": "Всего обработано файлов: {count}",
        "error_generate": "\nОшибка: {error}",
        "project_required": "Путь к проекту обязателен",
        "dir_not_exists": "Директория не существует: {path}",
        "doc_generated": "Документация успешно сгенерирована!",
        "cache_warning": "Это очистит файлы кэша. Продолжить? (y/n) [n]",
        "invalid_language": "Некорректный язык. Используйте 'en' или 'ru'",
        "language_changed": "Язык изменён на {lang}",
        "language_change_error": "Ошибка смены языка: {error}",
        "current_language": "Текущий язык: {lang}",
        "usage": "Использование: ofp lang [en|ru]",
        "current_working_directory": "Текущая рабочая директория",
        "unpack_required_args": "Ошибка: для распаковки требуется 2 аргумента - файл документации и целевая папка",
        "path_not_exists": "Ошибка: Путь '{path}' не существует!",
        "not_directory": "Ошибка: '{path}' не является директорией!",
        "loading_help_error": "Ошибка загрузки справки: {error}",
        "config_reset": "Файл конфигурации сброшен",
        "config_not_exists": "Файл конфигурации не существует",
        "reset_config_error": "Ошибка сброса конфигурации: {error}",
        "output_reset": "Выходной файл {path} сброшен",
        "output_not_exists": "Выходной файл {path} не существует",
        "reset_output_error": "Ошибка сброса выходного файла: {error}",
        "output_path_not_set": "Путь для выходного файла не задан в конфиге",
        "invalid_reset_option": "Некорректная опция сброса. Используйте -c для конфига или -o для выходного файла",
        "output_not_found": "Ошибка: Выходной файл не найден в конфиге или последних путях",
        "opened_output": "Выходной файл открыт: {path}",
        "open_file_error": "Ошибка открытия файла: {error}",
        "config_not_found": "Ошибка: Файл конфигурации не найден в стандартных или последних путях",
        "opened_config": "Файл конфигурации открыт: {path}",
        "open_config_error": "Ошибка открытия файла конфигурации: {error}",
        "loading_config_error": "Ошибка загрузки конфигурации: {error}",
        "saving_config_error": "Ошибка сохранения конфигурации: {error}",
        "config_saved": "Конфигурация успешно сохранена в {path}",
        "no_project_path": "Нельзя сохранить конфиг: путь к проекту не задан",
        "no_valid_config": "Ошибка: Не найден validный файл конфигурации",
        "using_parent_dir": "Используется родительская директория файла конфига как путь к проекту: {path}",
        "latest_paths_config": "Используется путь из последних путей: {path}",
        "file_creation_error": " Не удалось создать файл {file}: {error}",
        "unpack_success": " Проект успешно распакован в: {path}",
        "unpack_error": " Ошибка распаковки: {error}",
        "doc_section_not_found": "Ошибка: Не найден раздел с структурой проекта.",
        "file_not_found": "Ошибка: Файл документации '{path}' не найден",
        "target_not_empty": "Ошибка: Целевая директория '{path}' не пуста",
        "project_required": "Ошибка: Требуется указать путь к проекту!",
        "dir_not_exists": "Ошибка: Директория '{path}' не существует!",
        "doc_generated": "Документация успешно сгенерирована!",
        "output_file": "Выходной файл: {path}",
        "files_processed": "Всего обработано файлов: {count}",
        "scanning_structure": "Сканирование структуры проекта...",
        "generating_docs": "Генерация документации...",
        "doc_regenerated": "Документация перегенерирована успешно!",
        "cache_warning": " Весь кеш будет очищен!",
        "uninstall_deleted_dir": " Удалена директория: {path}",
        "uninstall_deleted_cmd": " Команда удалена: {cmd}",
        "uninstall_error": " Ошибка удаления: {error}",
        "unknown_command": " Неизвестная команда. Доступные команды: install, uninstall, update",
        "path_instructions_win": " Для работы команды из любого места:\n1. Нажмите Win+R, введите 'sysdm.cpl' и нажмите Enter\n2. Перейдите на вкладку 'Дополнительно'\n3. Нажмите 'Переменные среды'\n4. В разделе 'Системные переменные' найдите 'Path' и нажмите 'Изменить'\n5. Добавьте новый путь: {path}",
        "path_instructions_linux": " Добавьте в ~/.bashrc или ~/.zshrc:\nexport PATH=\"$PATH:{path}\"\nИ выполните: source ~/.bashrc"
    },
    "installer": {
        "install_start": " Установка программы в: {path}",
        "install_complete": " Установка завершена! Теперь используйте команду '{cmd}'",
        "install_error": " Ошибка установки: {error}",
        "deps_install": " Установка зависимостей из requirements.txt...",
        "deps_installed": " Зависимости успешно установлены",
        "deps_install_error": " Ошибка установки зависимостей: {error}",
        "deps_install_unknown": " Ошибка при установке зависимостей: {error}",
        "requirements_not_found": " Файл requirements.txt не найден, пропускаем установку зависимостей",
        "update_start": " Клонирование репозитория для обновления (текущая версия: {version})...",
        "update_complete": " Программа успешно обновлена с версии {old_version} до {new_version}!",
        "update_error": " Ошибка обновления: {error}",
        "git_error": " Ошибка при выполнении git: {error}",
        "not_installed": " Программа не установлена. Сначала выполните установку.",
        "uninstall_deleted_dir": " Удалена директория: {path}",
        "uninstall_deleted_cmd": " Команда удалена: {cmd}",
        "uninstall_error": " Ошибка удаления: {error}",
        "unknown_command": " Неизвестная команда. Доступные команды: install, uninstall, update",
        "path_instructions_win": " Для работы команды из любого места:\n1. Нажмите Win+R, введите 'sysdm.cpl' и нажмите Enter\n2. Перейдите на вкладку 'Дополнительно'\n3. Нажмите 'Переменные среды'\n4. В разделе 'Системные переменные' найдите 'Path' и нажмите 'Изменить'\n5. Добавьте новый путь: {path}",
        "path_instructions_linux": " Добавьте в ~/.bashrc или ~/.zshrc:\nexport PATH=\"$PATH:{path}\"\nИ выполните: source ~/.bashrc"
    },
    "tui": {
        "config_saved": "Конфигурация сохранена!",
        "json_error": "Ошибка в JSON: {error}",
        "generation_preparing": "Подготовка к генерации...",
        "generation_canceled": "Отменено",
        "generation_started": "Идёт генерация документации...",
        "generation_complete": "Генерация завершена!\n{result}",
        "generation_error": "Ошибка генерации: {error}",
        "opening_doc": "Открытие документации...",
        "doc_not_found_red": "Документация не найдена!",
        "doc_opened_green": "Документация открыта:\n{path}",
        "open_error_red": "Ошибка: {error}",
        "opening_config": "Попытка открыть конфиг...",
        "config_not_found_red": "Конфиг не найден!",
        "config_opened_green": "Конфиг открыт в {path}",
        "config_error_red": "Ошибка: {error}",
        "info_error": "Ошибка загрузки информации",
        "unpack_paths_required": "Укажите оба пути!",
        "unpack_error_red": "Ошибка: {error}",
        "app_title": "One File Project",
        "generate_button": "Сгенерировать документацию",
        "open_docs_button": "Открыть документацию",
        "config_button": "Конфигурация",
        "edit_config_button": "Редактировать конфиг",
        "unpack_button": "Распаковать проект",
        "info_button": "Информация",
        "view_md_button": "Просмотр Markdown",
        "language_button": "Сменить язык",
        "choose_language": "Выберите язык:",
        "footer_highlight_key": "КЛЮЧ",
        "doc_file_label": "Путь к файлу документации:",
        "target_dir_label": "Путь к целевой директории:",
        "unpack_button_confirm": "Распаковать",
        "enter_path": "Укажите путь или оставьте текущий",
        "path_input_title": "Укажите путь:",
        "confirm_path": "Подтвердить путь",
        "close": "Закрыть",
        "project_path_title": "Путь к проекту:",
        "output_path_title": "Путь для вывода:"
    },
    "utils": {
        "error_saving_latest_config": "Ошибка сохранения последней конфигурации: {error}",
        "error_loading_latest_config": "Ошибка загрузки последней конфигурации: {error}",
        "error_loading_latest_paths": "Ошибка загрузки последних путей: {error}",
        "error_loading_config": "Ошибка загрузки конфигурации: {error}",
        "cannot_save_config": "Невозможно сохранить конфигурацию: путь к проекту не задан",
        "config_saved_successfully": "Конфигурация успешно сохранена в {path}",
        "error_saving_config": "Ошибка сохранения конфигурации: {error}",
        "current_configuration": "Текущая конфигурация:",
        "edit_configuration": "Редактирование конфигурации:",
        "filter_settings": "Настройки фильтров:",
        "whitelist_settings": "Настройки белого списка:",
        "current_whitelist_paths": "Текущие пути белого списка (пусто означает все файлы):",
        "ignore_settings": "Настройки игнорирования:",
        "current_ignored_folders": "Текущие игнорируемые папки:",
        "current_ignored_files": "Текущие игнорируемые файлы:",
        "current_ignored_paths": "Текущие игнорируемые пути:",
        "project_path": "Путь к проекту",
        "output_file_path": "Путь к выходному файлу",
        "show_hidden_files": "Показывать скрытые файлы? (y/n) [n]:",
        "edit_question": "Редактировать? (y/n) [n]:",
        "enter_paths_to_include": "Введите пути для включения (через запятую, * для маски, относительно проекта):",
        "enter_folders_to_ignore": "Введите папки для игнорирования (через запятую):",
        "enter_file_patterns_to_ignore": "Введите шаблоны файлов для игнорирования (через запятую, * для маски):",
        "enter_full_paths_to_ignore": "Введите полные пути для игнорирования (через запятую, * для маски):"
    },
    "ui": {
        "header_title": "ДОКУМЕНТАЦИЯ ONE FILE PROJECT",
        "footer_help": "Справка: Нажмите ? для дополнительной информации"
    },
    "doc": {
        "structure_title": "Структура проекта",
        "files_content_title": "Содержимое файлов"
    }
}
```

---


## program/locales/ru.json.new

```text
{
    "common": {
        "header_title": "OneFileProject TUI",
        "error": "Ошибка",
        "success": "Успех",
        "warning": "Предупреждение",
        "info": "Информация",
        "canceled": "Операция отменена пользователем",
        "version": "Версия",
        "author": "Автор",
        "author_name": "Антон Алейниченко - https://aleynichenko.ru",
        "repository": "Репозиторий",
        "repository_url": "https://github.com/Antongo22/OneFileProject",
        "information": "Общая информация",
        "confirm": "Подтвердить",
        "cancel": "Отмена",
        "save": "Сохранить",
        "path": "Путь",
        "directory": "Директория",
        "file": "Файл"
    },
    "commands": {
        "error_loading_help": "Ошибка загрузки справки: {error}",
        "file_not_found": "Файл не найден: {path}",
        "target_not_empty": "Целевая директория не пуста: {path}",
        "doc_section_not_found": "Необходимая секция документации не найдена",
        "file_create_error": "Ошибка создания файла: {error}",
        "unpack_success": "Проект успешно распакован в {path}",
        "output_file_not_found": "Ошибка: Выходной файл не найден в конфигурации или последних путях",
        "opened_output_file": "Открыт выходной файл: {path}",
        "error_opening_file": "Ошибка открытия файла: {error}",
        "config_file_not_found": "Ошибка: Файл конфигурации не найден в стандартных или последних путях",
        "opened_config_file": "Открыт файл конфигурации: {path}",
        "error_opening_config": "Ошибка открытия файла конфигурации: {error}",
        "invalid_reset_option": "Неверная опция сброса. Используйте -c для конфигурации или -o для выходного файла",
        "config_reset": "Файл конфигурации был сброшен",
        "config_not_exist": "Файл конфигурации не существует",
        "error_resetting_config": "Ошибка сброса конфигурации: {error}",
        "output_not_set": "Выходной путь не задан в конфигурации",
        "output_reset": "Выходной файл {path} был сброшен",
        "output_not_exist": "Выходной файл {path} не существует",
        "error_resetting_output": "Ошибка сброса выходного файла: {error}",
        "error_loading_config_redo": "Ошибка загрузки конфигурации: {error}",
        "config_from_latest": "Пробую конфигурацию из последних путей: {path}",
        "latest_path_error": "Ошибка загрузки конфигурации из последних путей: {error}",
        "no_valid_config": "Ошибка: Не найдено действительного файла конфигурации",
        "using_parent_dir": "Использую родительскую директорию файла конфигурации как путь к проекту: {path}",
        "scanning_project": "\nСканирование структуры проекта...",
        "generating_doc": "\nГенерация документации...",
        "output_from_latest": "Использую выходной путь из последних путей: {path}",
        "doc_regenerated": "\nДокументация успешно перегенерирована!",
        "output_file": "Выходной файл: {path}",
        "files_processed": "Всего обработано файлов: {count}",
        "error_generate": "\nОшибка: {error}",
        "project_required": "Путь к проекту обязателен",
        "dir_not_exists": "Директория не существует: {path}",
        "doc_generated": "Документация успешно сгенерирована!",
        "invalid_language": "Неверный язык. Используйте 'en' или 'ru'",
        "language_changed": "Язык изменен на {lang}",
        "language_change_error": "Ошибка смены языка: {error}",
        "cache_warning": "Будут очищены кеш-файлы. Продолжить? (y/n) [n]",
        "current_language": "Текущий язык: {lang}",
        "usage": "Использование: ofp lang [en|ru]",
        "current_working_directory": "Текущая рабочая директория",
        "unpack_required_args": "Ошибка: для распаковки требуется 2 аргумента - файл документации и целевая папка",
        "path_not_exists": "Ошибка: Путь '{path}' не существует!",
        "not_directory": "Ошибка: '{path}' не является директорией!",
        "loading_help_error": "Ошибка загрузки справки: {error}",
        "config_not_exists": "Файл конфигурации не существует",
        "reset_config_error": "Ошибка сброса конфигурации: {error}",
        "output_not_exists": "Выходной файл {path} не существует",
        "output_opened": "Выходной файл открыт: {path}",
        "opened_output": "Выходной файл открыт: {path}",
        "open_file_error": "Ошибка открытия файла: {error}",
        "config_file_opened": "Файл конфигурации открыт: {path}",
        "opened_config": "Файл конфигурации открыт: {path}",
        "config_open_error": "Ошибка открытия файла конфигурации: {error}",
        "config_saved": "Конфигурация сохранена успешно в {path}",
        "saving_config_error": "Ошибка сохранения конфигурации: {error}",
        "latest_paths_config": "Используется путь из последних путей: {path}",
        "file_creation_error": "Не удалось создать файл {file}: {error}",
        "unpack_success_msg": "Проект успешно распакован в: {path}",
        "unpack_error": "Ошибка распаковки: {error}",
        "path_instructions_win": "Для работы команды откуда угодно:\n1. Нажмите Win+R, введите 'sysdm.cpl' и нажмите Enter\n2. Перейдите на вкладку 'Дополнительно'\n3. Нажмите на 'Переменные среды'\n4. В разделе 'Системные переменные' найдите 'Path' и нажмите 'Изменить'\n5. Добавьте новый путь: {path}",
        "path_instructions_linux": "Добавьте в ~/.bashrc или ~/.zshrc:\nexport PATH=\"$PATH:{path}\"\nИ выполните: source ~/.bashrc",
        "uninstall_deleted_dir": "Удалена директория: {path}",
        "uninstall_deleted_cmd": "Команда удалена: {cmd}",
        "uninstall_error": "Ошибка удаления: {error}"
    },
    "installer": {
        "install_start": "Установка программы в: {path}",
        "install_complete": "Установка завершена! Теперь используйте команду '{cmd}'",
        "install_error": "Ошибка установки: {error}",
        "dir_creation_error": "Не удалось создать директорию {path}: {error}",
        "file_copy_error": "Не удалось скопировать файл {file}: {error}",
        "cmd_creation_error": "Не удалось создать команду {cmd}: {error}",
        "update_warning": "Программа уже установлена в {path}",
        "update_confirm": "Обновить? (y/n) [n]",
        "update_start": "Обновление программы...",
        "update_git": "Обновление через git...",
        "update_clone": "Переустановка...",
        "git_error": "Ошибка при выполнении git: {error}",
        "not_installed": "Программа не установлена. Сначала выполните установку.",
        "path_instructions_win": "Для работы команды откуда угодно:\n1. Нажмите Win+R, введите 'sysdm.cpl' и нажмите Enter\n2. Перейдите на вкладку 'Дополнительно'\n3. Нажмите на 'Переменные среды'\n4. В разделе 'Системные переменные' найдите 'Path' и нажмите 'Изменить'\n5. Добавьте новый путь: {path}",
        "path_instructions_linux": "Добавьте в ~/.bashrc или ~/.zshrc:\nexport PATH=\"$PATH:{path}\"\nИ выполните: source ~/.bashrc"
    },
    "tui": {
        "config_saved": "Конфигурация сохранена!",
        "json_error": "Ошибка в JSON: {error}",
        "generation_preparing": "Подготовка к генерации...",
        "generation_canceled": "Отменено",
        "generation_started": "Идет генерация документации...",
        "generation_complete": "Генерация завершена!\n{result}",
        "generation_error": "Ошибка генерации: {error}",
        "opening_doc": "Открываю документацию...",
        "doc_not_found_red": "Документация не найдена!",
        "doc_opened_green": "Документация открыта:\n{path}",
        "open_error_red": "Ошибка: {error}",
        "opening_config": "Пытаюсь открыть конфигурацию...",
        "config_not_found_red": "Конфигурация не найдена!",
        "config_opened_green": "Конфигурация открыта в {path}",
        "config_error_red": "Ошибка: {error}",
        "info_error": "Ошибка загрузки информации",
        "unpack_paths_required": "Укажите оба пути!",
        "unpack_error_red": "Ошибка: {error}",
        "app_title": "One File Project",
        "generate_button": "Сгенерировать документацию",
        "open_docs_button": "Открыть документацию",
        "config_button": "Конфигурация",
        "edit_config_button": "Редактировать конфиг",
        "unpack_button": "Распаковать проект",
        "info_button": "Информация",
        "view_md_button": "Просмотр Markdown",
        "language_button": "Сменить язык",
        "choose_language": "Выберите язык:",
        "footer_highlight_key": "КЛЮЧ",
        "doc_file_label": "Путь к файлу документации:",
        "target_dir_label": "Путь к целевой директории:",
        "unpack_button_confirm": "Распаковать",
        "enter_path": "Укажите путь или оставьте текущий",
        "path_input_title": "Укажите путь:",
        "confirm_path": "Подтвердить путь",
        "close": "Закрыть",
        "project_path_title": "Путь к проекту:",
        "output_path_title": "Путь для вывода:"
    },
    "utils": {
        "error_saving_latest_config": "Ошибка сохранения последней конфигурации: {error}",
        "error_loading_latest_config": "Ошибка загрузки последней конфигурации: {error}",
        "error_loading_latest_paths": "Ошибка загрузки последних путей: {error}",
        "error_loading_config": "Ошибка загрузки конфигурации: {error}",
        "cannot_save_config": "Невозможно сохранить конфигурацию: путь к проекту не задан",
        "config_saved_successfully": "Конфигурация успешно сохранена в {path}",
        "error_saving_config": "Ошибка сохранения конфигурации: {error}",
        "current_configuration": "Текущая конфигурация:",
        "edit_configuration": "Редактирование конфигурации:",
        "filter_settings": "Настройки фильтров:",
        "whitelist_settings": "Настройки белого списка:",
        "current_whitelist_paths": "Текущие пути белого списка (пусто означает все файлы):",
        "ignore_settings": "Настройки игнорирования:",
        "current_ignored_folders": "Текущие игнорируемые папки:",
        "current_ignored_files": "Текущие игнорируемые файлы:",
        "current_ignored_paths": "Текущие игнорируемые пути:",
        "project_path": "Путь к проекту",
        "output_file_path": "Путь к выходному файлу",
        "show_hidden_files": "Показывать скрытые файлы? (y/n) [n]:",
        "edit_question": "Редактировать? (y/n) [n]:",
        "enter_paths_to_include": "Введите пути для включения (через запятую, * для маски, относительно проекта):",
        "enter_folders_to_ignore": "Введите папки для игнорирования (через запятую):",
        "enter_file_patterns_to_ignore": "Введите шаблоны файлов для игнорирования (через запятую, * для маски):",
        "enter_full_paths_to_ignore": "Введите полные пути для игнорирования (через запятую, * для маски):"
    },
    "ui": {
        "header_title": "ДОКУМЕНТАЦИЯ ONE FILE PROJECT",
        "footer_help": "Справка: Нажмите ? для дополнительной информации"
    },
    "doc": {
        "structure_title": "Структура проекта",
        "files_content_title": "Содержимое файлов"
    }
}

```

---


## program/translator.py

```python
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('translator')


class Translator:
    """Простой класс переводчика, который читает переводы из JSON файлов"""

    def __init__(self, locale_dir: str = "locales"):
        # Определяем абсолютный путь к папке переводов
        script_dir = Path(__file__).parent
        self.locale_dir = script_dir / locale_dir
        
        self.translations = {}
        self.current_lang = "en"
        self.default_lang = "en"

        # Создаем директорию переводов, если она не существует
        os.makedirs(self.locale_dir, exist_ok=True)
        self.load_translations()

    def load_translations(self):
        """Загружает переводы из JSON файлов"""
        for lang_file in self.locale_dir.glob("*.json"):
            lang = lang_file.stem
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    self.translations[lang] = json.load(f)
                    logger.debug(f"Загружен файл локализации: {lang}")
            except Exception as e:
                logger.error(f"Ошибка загрузки файла {lang_file}: {str(e)}")

    def set_language(self, lang: str):
        """Устанавливает текущий язык"""
        if lang in self.translations:
            self.current_lang = lang
            return True
        return False

    def translate(self, key: str, **kwargs):
        """
        Получает перевод по ключу
        :param key: Ключ в формате 'category.subcategory.key'
        :param kwargs: Параметры для форматирования
        """
        if not key:
            return key

        # Разбиваем ключ на части
        parts = key.split('.')

        # Получаем перевод из текущего языка
        result = self._find_translation(self.current_lang, parts)

        # Если перевод не найден, пробуем получить из языка по умолчанию
        if result is None and self.current_lang != self.default_lang:
            result = self._find_translation(self.default_lang, parts)

        # Если перевод все еще не найден, возвращаем последнюю часть ключа
        if result is None:
            result = parts[-1].replace('_', ' ').capitalize()

        # Применяем параметры форматирования
        if kwargs and isinstance(result, str):
            try:
                result = result.format(**kwargs)
            except Exception as e:
                logger.warning(f"Ошибка форматирования для {key}: {str(e)}")

        return result

    def _find_translation(self, lang, parts):
        """Находит перевод по частям ключа"""
        if lang not in self.translations:
            return None

        current = self.translations[lang]
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current if isinstance(current, str) else None


# Создаем глобальный экземпляр переводчика
translator = Translator()
```

---


## program/tui.py

```python
from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Button, Static, Input, TextArea, DirectoryTree
)
from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual import on, events
from pathlib import Path
import os
import json

from program import utils, config_utils as cfg

import program.commands as commands
from textual.widgets import Markdown as TextualMarkdown
from program.translator import translator

# Общий CSS для всего приложения, чтобы избежать выделения текста на кнопках
SHARED_CSS = """
/* Глобальный стиль для отключения выделения текста в кнопках */
Button:focus > .button--content {
    color: $text;
    text-style: none;
}

Button.-active > .button--content {
    color: $text;
    text-style: none;
}

/* Стиль для активной кнопки (выбранный элемент) */
Button.selected-lang {
    background: $accent;
}
"""


class ConfigEditor(Screen):
    """Экран редактирования конфигурации"""
    CSS = SHARED_CSS + """
    #config-container {
        width: 80%;
        height: 100%;
        margin: 1;
        border: solid $accent;
        padding: 1;
    }
    #config-editor {
        width: 100%;
        height: 80%;
    }
    Button {
        width: 20%;
        margin: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        config_path = utils.get_config_path()
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
        except FileNotFoundError:
            config_content = json.dumps(cfg.DEFAULT_CONFIG, indent=2)

        yield Container(
            TextArea(config_content, id="config-editor", language="json"),
            Button(translator.translate('common.save'), id="save-config", variant="primary"),
            Button(translator.translate('common.cancel'), id="cancel-config"),
            id="config-container"
        )

    @on(Button.Pressed, "#save-config")
    def save_config(self):
        editor = self.query_one("#config-editor")
        try:
            json.loads(editor.text)
            config_path = utils.get_config_path()
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(editor.text)
            self.notify(translator.translate('tui.config_saved'), severity="success")
            self.app.pop_screen()
        except json.JSONDecodeError as e:
            self.notify(translator.translate('tui.json_error', error=str(e)), severity="error")

    @on(Button.Pressed, "#cancel-config")
    def cancel_edit(self):
        self.app.pop_screen()


class PathInputScreen(Screen):
    CSS = SHARED_CSS + """
    #path-container {
        width: 80%;
        height: 24;
        min-height: 24; 
        margin: 1;
        border: solid $accent;
        padding: 2;
    }

    Static {
        width: 100%;
        margin-bottom: 1;
    }
    Input {
        width: 100%;
        margin-bottom: 2;
    }
    Button {
        width: 20%;
        margin: 1 2;
    }
    """

    def __init__(self, title: str, default: str = None):
        super().__init__()
        self.title = title
        self.default = default or os.getcwd()

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title),
            Input(value=self.default, placeholder=translator.translate('tui.enter_path'), id="path-input"),
            Button(translator.translate('tui.confirm_path'), id="confirm-path", variant="primary"),
            Button(translator.translate('common.cancel'), id="cancel-path"),
            id="path-container"
        )

    @on(Button.Pressed, "#confirm-path")
    def confirm_path(self):
        path_input = self.query_one("#path-input")
        input_value = path_input.value.strip()

        if input_value == ".":
            input_value = os.getcwd()
        elif not input_value:
            input_value = self.default

        self.dismiss(input_value)

    @on(Button.Pressed, "#cancel-path")
    def cancel_path(self):
        self.dismiss(None)


class UnpackScreen(Screen):
    """Экран распаковки проекта"""
    CSS = SHARED_CSS + """
    #unpack-container {
        width: 80%;
        height: auto;
        min-height: 16;
        margin: 1;
        border: solid $accent;
        padding: 2;
    }
    #unpack-container > Static {
        width: 100%;
        margin-bottom: 1;
    }
    #unpack-container > Input {
        width: 100%;
        margin-bottom: 2;
    }
    #unpack-container > Button {
        width: 20%;
        margin: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Container(
            Static(translator.translate('tui.doc_file_label')),
            Input(placeholder="/path/to/documentation.md", id="doc-path"),
            Static(translator.translate('tui.target_dir_label')),
            Input(placeholder="/path/to/target/directory", id="target-path"),
            Button(translator.translate('tui.unpack_button_confirm'), id="do-unpack", variant="primary"),
            Button(translator.translate('common.cancel'), id="cancel-unpack"),
            id="unpack-container"
        )

    @on(Button.Pressed, "#do-unpack")
    def do_unpack(self):
        doc_input = self.query_one("#doc-path")
        target_input = self.query_one("#target-path")

        doc_path = doc_input.value.strip()
        target_path = target_input.value.strip()

        if not doc_path or not target_path:
            self.notify(translator.translate('tui.unpack_paths_required'), severity="error")
            return

        try:
            result = commands.unpack(doc_path, target_path)
            if result[0]:
                self.notify(result[1], severity="success")
                self.app.pop_screen()
            else:
                self.notify(translator.translate('tui.unpack_error_red', error=result[1]), severity="error")
        except Exception as e:
            self.notify(translator.translate('tui.unpack_error_red', error=str(e)), severity="error")

    @on(Button.Pressed, "#cancel-unpack")
    def cancel_unpack(self):
        self.app.pop_screen()


class LanguageScreen(Screen):
    """Экран выбора языка"""
    CSS = SHARED_CSS + """
    #lang-container {
        width: 30%;
        height: 15;
        margin: 1;
        border: solid $accent;
        padding: 2;
    }
    #lang-container > Static {
        width: 100%;
        margin-bottom: 1;
        text-align: center;
    }
    #cancel-button-container {
        width: 100%;
        align: center middle;
    }
    #cancel-lang {
        width: 25%;
        margin: 1 0;
        /* Отключение выделения текста не поддерживается в Textual */
    }
    
    Button {
        /* Отключение выделения текста не поддерживается в Textual */
    }
    #lang-buttons {
        layout: horizontal;
        width: 100%;
        align: center middle;
    }
    .selected-lang {
        background: $accent;
    }
    """
    
    def compose(self) -> ComposeResult:
        # Получаем текущий язык
        current_lang = translator.current_lang
        
        yield Container(
            Static(translator.translate('tui.choose_language')),
            Container(
                Button(
                    "English", 
                    id="lang-en",
                    classes="selected-lang" if current_lang == "en" else ""
                ),
                Button(
                    "Русский", 
                    id="lang-ru",
                    classes="selected-lang" if current_lang == "ru" else ""
                ),
                id="lang-buttons"
            ),
            Container(
                Button(translator.translate('common.cancel'), id="cancel-lang"),
                id="cancel-button-container"
            ),
            id="lang-container"
        )
    
    @on(Button.Pressed, "#lang-en")
    def set_english(self):
        global restart_required
        
        success, message = commands.change_language("en")
        if success:
            # Устанавливаем флаг необходимости перезапуска
            restart_required = True
            
            # Закрываем этот экран
            self.app.pop_screen()
            
            # Сразу закрываем приложение для перезапуска
            self.app.exit()
        else:
            self.notify(message, severity="error")
            self.app.pop_screen()

    @on(Button.Pressed, "#lang-ru")
    def set_russian(self):
        global restart_required
        
        success, message = commands.change_language("ru")
        if success:
            # Устанавливаем флаг необходимости перезапуска
            restart_required = True
            
            # Закрываем этот экран
            self.app.pop_screen()
            
            # Сразу закрываем приложение для перезапуска
            self.app.exit()
        else:
            self.notify(message, severity="error")
            self.app.pop_screen()
        
    @on(Button.Pressed, "#cancel-lang")
    def cancel_lang(self):
        self.app.pop_screen()


class MarkdownViewer(Screen):
    """Экран для просмотра Markdown с форматированием"""
    CSS = SHARED_CSS + """
    Screen {
        align: center middle;
    }

    #md-content {
        width: 95%;
        height: 85%;
        layout: vertical;
        align: center top;
    }

    #md-viewer {
        width: 100%;
        height: 85%;
        border: solid $accent;
        padding: 1;
    }

    #close-button-container {
        width: 100%;
        height: auto;
        margin-top: 1;
        align: center middle;
    }

    #close-viewer {
        width: 15%;
        margin: 1;
        /* Отключение выделения текста не поддерживается в Textual */
    }
    
    Button {
        /* Отключение выделения текста не поддерживается в Textual */
    }
    """
    
    def __init__(self, content: str):
        super().__init__()
        self.content = self.sanitize_markdown(content)

    def sanitize_markdown(self, text: str) -> str:
        """Очистка Markdown от ANSI кодов и проблемных символов"""
        text = text.replace("[/]", "").replace("[red]", "").replace("[green]", "")
        return text

    def compose(self) -> ComposeResult:
        # Создаем контейнер для всего содержимого
        with Container(id="md-content"):
            # Markdown в скроллируемом контейнере
            yield ScrollableContainer(
                TextualMarkdown(self.content),
                id="md-viewer"
            )
            # Отдельный контейнер для кнопки
            with Container(id="close-button-container"):
                yield Button(translator.translate('common.close'), id="close-viewer")

    @on(Button.Pressed, "#close-viewer")
    def close_viewer(self):
        self.app.pop_screen()


class OFPTUI(App):
    """Главный TUI интерфейс"""
    CSS = SHARED_CSS + """
    Screen {
        layout: vertical;
        align: center middle;
    }
    #buttons {
        layout: vertical;
        width: 100%;
        height: auto;
        align: center middle;
    }
    #button-row1, #button-row2 {
        layout: horizontal;
        width: 100%;
        height: auto;
        align: center middle;
        margin: 1 0;
    }
    Button {
        width: 15%;
        margin: 0 1;
    }
    
    /* Убираем выделение текста при нажатии */
    Button:focus > .button--content {
        color: $text;
        text-style: none;
    }
    
    Button.-active > .button--content {
        color: $text;
        text-style: none;
    }
    #content {
        width: 95%;
        height: 30;
        border: solid $accent;
        margin: 1;
        padding: 1;
        background: $boost;
        overflow: auto;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Exit"),
    ]

    def compose(self) -> ComposeResult:
        # Создаем Header и Footer без параметров, а затем настраиваем их
        yield Header(id="header", name="header")
        yield Footer(id="footer", name="footer")

        with Container(id="buttons"):
            # Первый ряд кнопок
            with Container(id="button-row1"):
                yield Button(translator.translate('tui.generate_button'), id="generate", variant="primary")
                yield Button(translator.translate('tui.open_docs_button'), id="open_doc")
                yield Button(translator.translate('tui.config_button'), id="open-config")
                yield Button(translator.translate('tui.edit_config_button'), id="edit-config")
            
            # Второй ряд кнопок
            with Container(id="button-row2"):
                yield Button(translator.translate('tui.unpack_button'), id="unpack")
                yield Button(translator.translate('tui.info_button'), id="info")
                yield Button(translator.translate('tui.view_md_button'), id="view_md")
                yield Button(translator.translate('tui.language_button'), id="change-lang")

        yield Static(translator.translate('tui.app_title'), id="content")
        
    def on_mount(self) -> None:
        """Настраиваем заголовок и нижний колонтитул после монтирования"""
        # Получаем компоненты по их ID
        header = self.query_one("#header", Header)
        footer = self.query_one("#footer", Footer)
        
        # Устанавливаем текст
        header.tall = True
        header.title = translator.translate('ui.header_title')
        
        # Настраиваем текст подсказки в нижнем колонтитуле
        footer.highlight_key = "?"
        footer.highlight_name = translator.translate('ui.footer_help')

    def action_quit(self):
        self.exit()

    @on(Button.Pressed, "#generate")
    async def on_generate(self) -> None:
        """Генерация документации"""
        content = self.query_one("#content")
        content.update(translator.translate('tui.generation_preparing'))

        project_screen = PathInputScreen(
            translator.translate('tui.project_path_title'),
            utils.load_config().get('project_path')
        )

        def handle_project_path(project_path: str | None) -> None:
            if not project_path:
                content.update(translator.translate('tui.generation_canceled'))
                return

            content.update(translator.translate('tui.generation_started'))

            project_path_obj = Path(project_path)
            default_output = str(project_path_obj / "project_documentation.md")

            output_screen = PathInputScreen(translator.translate('tui.output_path_title'), default_output)

            def handle_output_path(output_path: str | None) -> None:
                if not output_path:
                    content.update(translator.translate('tui.generation_canceled'))
                    return

                content.update(translator.translate('tui.generation_started'))
                try:
                    result = commands.generate_documentation(project_path, output_path)
                    clean_result = commands.ansi_to_textual(result)
                    content.update(translator.translate('tui.generation_complete', result=clean_result))

                    config = utils.load_config()
                    config['project_path'] = project_path
                    config['output_path'] = output_path
                    utils.save_config(config)

                except Exception as e:
                    content.update(translator.translate('tui.generation_error', error=str(e)))

            self.push_screen(output_screen, handle_output_path)

        self.push_screen(project_screen, handle_project_path)

    @on(Button.Pressed, "#open_doc")
    async def open_documentation(self) -> None:
        """Открытие документации"""
        content = self.query_one("#content")
        content.update(translator.translate('tui.opening_doc'))

        try:
            path = commands.open_output_file()

            if not path:
                content.update(f"[red]{translator.translate('tui.doc_not_found_red')}[/]")
                return

            content.update(f"[green]{translator.translate('tui.doc_opened_green', path=path)}[/]")
        except Exception as e:
            content.update(f"[red]{translator.translate('tui.open_error_red', error=str(e))}[/]")


    @on(Button.Pressed, "#open-config")
    async def on_open_config(self):
        """Открытие конфига"""
        content = self.query_one("#content")
        content.update(translator.translate('tui.opening_config'))
        try:
            path = commands.open_config_file()

            if not path:
                content.update(f"[red]{translator.translate('tui.config_not_found_red')}[/]")
                return

            content.update(f"[green]{translator.translate('tui.config_opened_green', path=path)}[/]")
        except Exception as e:
            content.update(f"[red]{translator.translate('tui.config_error_red', error=str(e))}[/]")

    @on(Button.Pressed, "#edit-config")
    async def on_edit_config(self):
        """Редактирование конфига"""
        await self.push_screen(ConfigEditor())

    @on(Button.Pressed, "#unpack")
    async def on_unpack(self):
        """Распаковка проекта"""
        await self.push_screen(UnpackScreen())



    @on(Button.Pressed, "#info")
    async def on_info(self):
        content = self.query_one("#content")
        try:
            info = commands.ansi_to_textual(commands.print_project_info())
            content.update(info)
        except Exception as e:
            content.update(translator.translate('tui.info_error'))


    @on(Button.Pressed, "#view_md")
    async def view_markdown(self):
        """Открыть Markdown в отдельном экране"""
        try:
            path = commands.open_output_file(False)

            if not path:
                content = self.query_one("#content")
                content.update("[red]Документация не найдена![/]")
                return

            if path and os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    await self.push_screen(MarkdownViewer(content))
        except Exception as e:
            error_msg = str(e).replace("[", "").replace("]", "")
            self.notify(translator.translate('tui.open_error_red', error=error_msg), severity="error")
            
    def update_interface_language(self):
        """Обновляет язык интерфейса без перезапуска приложения"""
        # Запоминаем текущее состояние для восстановления
        try:
            current_content = self.query_one("#content").render()
        except Exception:
            current_content = translator.translate('tui.app_title')
        
        # Обновляем заголовок
        header = self.query_one("#header", Header)
        header.title = translator.translate('common.header_title')
        
        # Обновляем футер
        footer = self.query_one("#footer", Footer)
        footer.highlight_key = translator.translate('tui.footer_highlight_key')
        
        # Обновляем тексты на всех кнопках
        # Первый ряд
        self.query_one("#generate").label = translator.translate('tui.generate_button')
        self.query_one("#open_doc").label = translator.translate('tui.open_docs_button')
        self.query_one("#open-config").label = translator.translate('tui.config_button')
        self.query_one("#edit-config").label = translator.translate('tui.edit_config_button')
        # Второй ряд
        self.query_one("#unpack").label = translator.translate('tui.unpack_button')
        self.query_one("#info").label = translator.translate('tui.info_button')
        self.query_one("#view_md").label = translator.translate('tui.view_md_button')
        self.query_one("#change-lang").label = translator.translate('tui.language_button')
        
        # Восстанавливаем содержимое
        content = self.query_one("#content")
        content.update(current_content)
        
    @on(Button.Pressed, "#change-lang")
    async def on_change_language(self):
        """Смена языка интерфейса"""
        await self.push_screen(LanguageScreen())

# Глобальная переменная для отслеживания необходимости перезапуска
restart_required = False

def run_tui():
    """Запуск TUI интерфейса"""
    global restart_required
    
    # Запускаем приложение
    app = OFPTUI()
    app.run()
    
    # Если требуется перезапуск, запускаем TUI снова
    if restart_required:
        restart_required = False
        run_tui()

```

---


## program/utils.py

```python
import os
import json
from pathlib import Path
from typing import Tuple, Optional
import fnmatch
from colorama import init, Style
import program.config_utils as cfg
from program.translator import translator

init(autoreset=True)



def save_latest_paths(output_path: str, config: dict):
    """Сохраняет пути к последним использованным файлам и настройки"""
    output_dir = Path(output_path).parent

    config_in_output_dir = str(output_dir / "project_documenter_config.json")

    latest_config = {
        'config_path': config_in_output_dir,
        'output_path': output_path,
        'language': config.get('language', 'en')
    }

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(cfg.LATEST_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(latest_config, f, indent=2)
    except Exception as e:
        print(color_text(translator.translate('utils.error_saving_latest_config', error=str(e)), 'error'))


def load_latest_config() -> dict:
    """Загружает последние использованные настройки"""
    try:
        if os.path.exists(cfg.LATEST_CONFIG_FILE):
            with open(cfg.LATEST_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return {**cfg.DEFAULT_LATEST_CONFIG, **json.load(f)}
        return cfg.DEFAULT_LATEST_CONFIG.copy()
    except Exception as e:
        print(color_text(translator.translate('utils.error_loading_latest_config', error=str(e)), 'error'))
        return cfg.DEFAULT_LATEST_CONFIG.copy()


def load_latest_paths() -> dict:
    """Загружает последние использованные пути из директории программы"""
    try:
        if os.path.exists(cfg.LATEST_CONFIG_FILE):
            with open(cfg.LATEST_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(color_text(translator.translate('utils.error_loading_latest_paths', error=str(e)), 'error'))
        return {}

def color_text(text: str, color_type: str) -> str:
    """Возвращает цветной текст для консоли"""
    return f"{cfg.COLORS.get(color_type, '')}{text}{Style.RESET_ALL}"


def load_config() -> dict:
    """Загружает конфигурацию без рекурсии"""
    try:
        config_path = Path(cfg.CONFIG_FILE)
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('project_path'):
                    project_config_path = Path(config['project_path']) / cfg.CONFIG_FILE
                    if not project_config_path.exists():
                        project_config_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(project_config_path, 'w', encoding='utf-8') as pf:
                            json.dump(config, pf, indent=2)
                        config_path.unlink()
                return {**cfg.DEFAULT_CONFIG, **config}

        project_config_path = Path(cfg.DEFAULT_CONFIG['project_path']) / cfg.CONFIG_FILE if cfg.DEFAULT_CONFIG['project_path'] else None
        if project_config_path and project_config_path.exists():
            with open(project_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {**cfg.DEFAULT_CONFIG, **config}

        return cfg.DEFAULT_CONFIG.copy()
    except Exception as e:
        print(color_text(translator.translate('utils.error_loading_config', error=str(e)), 'error'))
        return cfg.DEFAULT_CONFIG.copy()


def should_ignore(path: str, rel_path: str, config: dict) -> bool:
    """Проверяет нужно ли игнорировать файл/папку"""
    name = os.path.basename(path)
    rel_path = rel_path.replace('\\', '/')
    is_dir = os.path.isdir(path)

    if config.get('whitelist_paths') and config['whitelist_paths']:
        match_found = False
        for pattern in config['whitelist_paths']:
            norm_pattern = pattern.replace('\\', '/').rstrip('/') + '/'
            if rel_path.startswith(norm_pattern) or norm_pattern.startswith(rel_path + '/'):
                match_found = True
                break
        if not match_found:
            return True

    if not config['show_hidden'] and name.startswith('.'):
        return True

    for ignore_pattern in config['ignore_paths']:
        if fnmatch.fnmatch(rel_path, ignore_pattern):
            return True

    if is_dir:
        return any(ignore in rel_path.split('/') for ignore in config['ignore_folders'])

    return any(fnmatch.fnmatch(name, pattern) for pattern in config['ignore_files'])


def get_language(extension: str) -> str:
    """Определяет язык для подсветки синтаксиса"""
    return cfg.LANGUAGE_MAPPING.get(extension.lower(), 'text')

def get_config_path(config: Optional[dict] = None) -> Path:
    """Возвращает путь к файлу конфигурации"""
    if config and config.get('project_path'):
        return Path(config['project_path']) / cfg.CONFIG_FILE
    return Path(cfg.CONFIG_FILE)



def save_config(config: dict):
    """Сохраняет конфигурацию в файл"""
    try:
        if not config.get('project_path'):
            print(color_text(translator.translate('utils.cannot_save_config'), 'error'))
            return

        output_file = Path(config['output_path']).name
        if output_file not in config['ignore_files']:
            config['ignore_files'].append(output_file)

        config_path = Path(config['project_path']) / cfg.CONFIG_FILE
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        print(color_text(translator.translate('utils.config_saved_successfully', path=config_path), 'success'))
    except Exception as e:
        print(color_text(translator.translate('utils.error_saving_config', error=str(e)), 'error'))


def get_input(prompt: str, default: Optional[str] = None) -> str:
    """Получает ввод от пользователя с цветными подсказками"""
    if default:
        prompt = color_text(f"{prompt} [{default}]: ", 'info')
    else:
        prompt = color_text(f"{prompt}: ", 'info')
    return input(prompt).strip() or default




def generate_file_tree(root_path: str, config: dict, current_path: str = None, prefix: str = '') -> Tuple[ str, list[dict[str, str]]]:
    """Генерирует дерево файлов"""
    if current_path is None:
        current_path = root_path

    files_info = []
    tree = []

    if not os.path.isdir(current_path):
        return '', files_info

    contents = sorted(os.listdir(current_path))
    pointers = ['├── '] * (len(contents) - 1) + ['└── ']

    for pointer, name in zip(pointers, contents):
        full_path = os.path.join(current_path, name)
        rel_path = os.path.relpath(full_path, start=root_path).replace('\\', '/')

        if should_ignore(full_path, rel_path, config):
            continue

        if os.path.isdir(full_path):
            tree.append(f"{prefix}{pointer}{name}/")
            subtree, sub_files = generate_file_tree(root_path, config, full_path,
                                                    prefix + ('│   ' if pointer == '├── ' else '    '))
            tree.append(subtree)
            files_info.extend(sub_files)
        else:
            tree.append(f"{prefix}{pointer}{name}")
            file_ext = os.path.splitext(name)[1]
            files_info.append({
                'path': full_path,
                'rel_path': rel_path,
                'extension': file_ext,
                'language': get_language(file_ext)
            })

    return '\n'.join(tree), files_info



def extract_code_blocks(content: str) -> str:
    """Извлекает блоки кода из Markdown"""
    lines = content.split('\n')
    result = []
    in_block = False
    lang = ''
    block = []

    for line in lines:
        if line.startswith('```') and not in_block:
            in_block = True
            lang = line[3:].strip()
        elif line.startswith('```') and in_block:
            in_block = False
            if lang:
                result.append(f"```{lang}")
                result.extend(block)
                result.append("```\n")
            block = []
            lang = ''
        elif in_block:
            block.append(line)
        else:
            result.append(line)

    return '\n'.join(result)


def get_file_contents(files_info: list[dict[str, str]]) -> str:
    """Получает содержимое файлов"""
    contents = []
    for file_info in files_info:
        try:
            with open(file_info['path'], 'r', encoding='utf-8') as f:
                content = f.read()
                if file_info['extension'] == '.md':
                    content = extract_code_blocks(content)
        except UnicodeDecodeError:
            try:
                with open(file_info['path'], 'r', encoding='latin-1') as f:
                    content = f.read()
            except:
                content = "Binary file or unsupported encoding"
        except Exception as e:
            content = f"Error reading file: {str(e)}"

        contents.append(
            f"## {file_info['rel_path']}\n\n"
            f"```{file_info['language']}\n"
            f"{content}\n"
            f"```\n\n"
            f"---\n\n"
        )
    return '\n'.join(contents)


def edit_config(config: dict, cli_project_path: str = None) -> dict:
    """Интерактивное редактирование конфигурации"""
    if cli_project_path:
        project_path = os.path.abspath(cli_project_path)
        config['project_path'] = project_path
        if config['output_path'] == cfg.DEFAULT_CONFIG['output_path']:
            config['output_path'] = str(Path(project_path) / "project_documentation.md")
        return config

    print(color_text(f"\n{translator.translate('utils.current_configuration')}", 'highlight'))
    print(json.dumps(config, indent=2))

    print(color_text(f"\n{translator.translate('utils.edit_configuration')}", 'highlight'))
    config['project_path'] = get_input(translator.translate('utils.project_path'), config['project_path'])

    if config['project_path'] and config['output_path'] == cfg.DEFAULT_CONFIG['output_path']:
        config['output_path'] = str(Path(config['project_path']) / "project_documentation.md")

    config['output_path'] = get_input(translator.translate('utils.output_file_path'), config['output_path'])

    print(color_text(f"\n{translator.translate('utils.filter_settings')}", 'highlight'))
    config['show_hidden'] = input(color_text(translator.translate('utils.show_hidden_files'), 'info')).lower() == 'y'

    print(color_text(f"\n{translator.translate('utils.whitelist_settings')}", 'highlight'))
    print(color_text(translator.translate('utils.current_whitelist_paths'), 'info'),
          ', '.join(config.get('whitelist_paths', [])))
    if input(color_text(translator.translate('utils.edit_question'), 'info')).lower() == 'y':
        new_paths = input(
            color_text(translator.translate('utils.enter_paths_to_include'), 'info'))
        config['whitelist_paths'] = [p.strip() for p in new_paths.split(',') if p.strip()]

    print(color_text(f"\n{translator.translate('utils.ignore_settings')}", 'highlight'))
    print(color_text(translator.translate('utils.current_ignored_folders'), 'info'), ', '.join(config['ignore_folders']))
    if input(color_text(translator.translate('utils.edit_question'), 'info')).lower() == 'y':
        new_folders = input(color_text(translator.translate('utils.enter_folders_to_ignore'), 'info'))
        config['ignore_folders'] = [f.strip() for f in new_folders.split(',') if f.strip()] or config['ignore_folders']

    print(color_text(f"\n{translator.translate('utils.current_ignored_files')}", 'info'), ', '.join(config['ignore_files']))
    if input(color_text(translator.translate('utils.edit_question'), 'info')).lower() == 'y':
        new_files = input(color_text(translator.translate('utils.enter_file_patterns_to_ignore'), 'info'))
        config['ignore_files'] = [f.strip() for f in new_files.split(',') if f.strip()] or config['ignore_files']

    print(color_text(f"\n{translator.translate('utils.current_ignored_paths')}", 'info'), ', '.join(config['ignore_paths']))
    if input(color_text(translator.translate('utils.edit_question'), 'info')).lower() == 'y':
        new_paths = input(color_text(translator.translate('utils.enter_full_paths_to_ignore'), 'info'))
        config['ignore_paths'] = [p.strip() for p in new_paths.split(',') if p.strip()] or config['ignore_paths']

    return config

```

---


## requirements.txt

```text
colorama~=0.4.6
textual~=3.0.0
typing~=3.7.4.3
```

---

