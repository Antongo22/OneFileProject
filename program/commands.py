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


def init_config(dir_path: str = None, open_file: bool = False, remake: bool = False) -> tuple[bool, str]:
    """
    Создает стандартный конфигурационный файл в указанной директории
    
    Args:
        dir_path: Путь к директории, в которой нужно создать файл
        open_file: Если True, открывает файл в приложении по умолчанию
        remake: Если True, пересоздаёт файл, даже если он уже существует
        
    Returns:
        tuple: (успех операции (bool), сообщение)
    """
    try:
        if dir_path is None:
            return False, translator.translate('commands.specify_directory')

        if not os.path.exists(dir_path):
            return False, translator.translate('commands.directory_not_exists', path=dir_path)
            
        if not os.path.isdir(dir_path):
            return False, translator.translate('commands.not_directory', path=dir_path)

        config_path = os.path.join(dir_path, cfg.CONFIG_FILE)

        if os.path.exists(config_path):
            if remake:
                try:
                    os.remove(config_path)
                except Exception as e:
                    return False, translator.translate('commands.config_delete_error', path=config_path, error=str(e))
            else:
                return False, translator.translate('commands.config_already_exists', path=config_path)

        default_config = cfg.DEFAULT_CONFIG.copy()
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
            
        success_msg = translator.translate('commands.config_created', path=config_path)

        if open_file:
            open_config_file()
            open_msg = translator.translate('commands.file_opened', path=config_path)
            print(utils.color_text(open_msg, 'info'))
            
        return True, success_msg
    except Exception as e:
        error_msg = translator.translate('commands.config_init_error', error=str(e))
        print(utils.color_text(error_msg, 'error'))
        return False, error_msg
    
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
    print(utils.color_text(translator.translate('commands.generating_tree', path=directory_path, default=f"Generating directory tree for: {directory_path}"), 'info'))
    try:
        if not os.path.exists(directory_path):
            return utils.color_text(translator.translate("commands.path_not_exists", path=directory_path), 'error')
        if not os.path.isdir(directory_path):
            return utils.color_text(translator.translate("commands.not_directory", path=directory_path), 'error')
            
        directory_path = os.path.abspath(directory_path)
        root_name = os.path.basename(directory_path)
        
        config = {
            'ignore_folders': ['.git', '__pycache__', '.venv', 'node_modules'],
            'ignore_files': ['*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.exe'],
            'ignore_paths': [],
            'show_hidden': False,
            'whitelist_paths': []
        }
        
        user_config = utils.load_config()
        if user_config:
            for key in ['ignore_folders', 'ignore_files', 'ignore_paths', 'show_hidden', 'whitelist_paths']:
                if key in user_config:
                    config[key] = user_config[key]
        
        def build_tree(path, prefix=''):
            files = []
            dirs = []
            
            try:
                for item in sorted(os.listdir(path)):
                    full_path = os.path.join(path, item)
                    rel_path = os.path.relpath(full_path, directory_path)
                    
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
            
            for i, d in enumerate(dirs):
                idx += 1
                is_last = (idx == count)
                current_prefix = "└── " if is_last else "├── "
                next_prefix = "    " if is_last else "│   "
                full_path = os.path.join(path, d)
                tree += f"{prefix}{current_prefix}{d}/\n"
                tree += build_tree(full_path, prefix + next_prefix)
        
            for i, f in enumerate(files):
                idx += 1
                is_last = (idx == count)
                tree += f"{prefix}{'└── ' if is_last else '├── '}{f}\n"
            
            return tree
        
        tree = build_tree(directory_path)
        result = f"\n{root_name}/\n{tree}"
        return utils.color_text(result, 'highlight')
    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        return utils.color_text(f"\n{translator.translate('common.error')}: {str(e)}\n{trace}", 'error')
