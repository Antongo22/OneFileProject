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
        for cmd, desc in texts['commands_list']:
            help_text += f"\n    {utils.color_text(cmd, 'path')}{' ' * (20 - len(cmd))}{desc}"
        help_text += f"\n\n{utils.color_text(texts['examples'], 'info')}"
        for ex, desc in texts['examples_list']:
            help_text += f"\n    {utils.color_text(ex, 'highlight')}{' ' * (30 - len(ex))}{desc}"
        print(f"\n{help_text}\n")
    except Exception as e:
        print(utils.color_text(f"\nError loading help: {str(e)}\n", 'error'))


def print_project_info() -> str:
    """Выводит информацию о проекте с цветным оформлением"""
    return f"""
{utils.color_text(translator.translate("common.information", ), 'info')}
{utils.color_text("Author:", 'info')} {utils.color_text("Anton Aleynichenko - https://aleynichenko.ru", 'highlight')}
{utils.color_text("Repository:", 'info')} {utils.color_text("https://github.com/Antongo22/OneFileProject", 'highlight')}
{utils.color_text("Version:", 'info')} {utils.color_text(cfg.VERSION, 'highlight')}
"""


def unpack(doc_file: str, target_dir: str) -> (bool, Optional[str]):
    """Распаковывает проект из файла документации"""

    res = ""
    try:
        doc_path = Path(doc_file.strip('"\''))
        target_path = Path(target_dir.strip('"\''))

        if not doc_path.exists():
            return False, utils.color_text(f"Error: The documentation file '{doc_path}' was not found", 'error')

        if target_path.exists() and any(target_path.iterdir()):
            return False, utils.color_text(f"Error: The target directory '{target_path}' is not empty", 'error')

        target_path.mkdir(parents=True, exist_ok=True)

        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        structure_match = re.search(
            r'# (?:Структура проекта|Project Structure):.*?\n```.*?\n(.*?)\n```',
            content,
            re.DOTALL
        )

        if not structure_match:
            return False,utils.color_text("Error: The section with the project structure was not found.", 'error')

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
                 res += utils.color_text(f"⚠️ Failed to create {rel_path} file: {str(e)}", 'warning') + "\n"

        res += utils.color_text(f"✅ The project has been successfully unpacked in: {target_path}", 'success') + "\n"
        return True, res
    except Exception as e:
        res += utils.color_text(f"❌ Unpacking error: {str(e)}", 'error')
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
        return utils.color_text("Error: Project path is required!", 'error')

    if not os.path.isdir(project_path):
        return utils.color_text(f"Error: Directory '{project_path}' does not exist!", 'error')

    try:
        root_path = os.path.normpath(project_path)
        root_name = os.path.basename(root_path)

        config['project_path'] = project_path
        config['output_path'] = output_path

        tree, files = utils.generate_file_tree(root_path, config)

        md_content = (
            f"# Project Structure: {root_name}\n\n"
            f"```\n{root_name}/\n{tree}\n```\n\n"
            f"# Files Content\n\n{utils.get_file_contents(files)}"
        )

        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path_obj, 'w', encoding='utf-8') as f:
            f.write(md_content)

        utils.save_config(config)
        utils.save_latest_paths(str(output_path_obj), utils.load_latest_config())

        result = (
            f"{utils.color_text('Documentation generated successfully!', 'success')}\n"
            f"{utils.color_text(f'Output file: {output_path}', 'path')}\n"
            f"{utils.color_text(f'Total files processed: {len(files)}', 'info')}"
        )
        return result

    except Exception as e:
        return utils.color_text(f"\nError: {str(e)}", 'error')


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
        return False, "Invalid language. Use 'en' or 'ru'"

    try:
        latest_config = utils.load_latest_config()
        latest_config['language'] = lang
        with open(cfg.LATEST_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(latest_config, f, indent=2)
        return True, f"Language changed to {lang}"
    except Exception as e:
        return False, f"Error changing language: {str(e)}"
