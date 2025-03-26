import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import fnmatch
from colorama import init, Fore, Style
import signal
import re

import installer

init(autoreset=True)

PROGRAM_NAME = "ofp"
CONFIG_FILE = "project_documenter_config.json"
LATEST_PATHS_FILE = str(Path(__file__).parent / "latest_paths.json")


def get_version():
    """Получает версию из файла version или возвращает v0.0.0 при ошибке"""
    try:
        with open(Path(__file__).parent / 'version', 'r') as f:
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
    'ignore_folders': ['.git', '__pycache__', 'node_modules', 'venv'],
    'ignore_files': [
        '.gitignore', '.env', CONFIG_FILE, '*.md',
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


def save_latest_paths(output_path: str):
    """Сохраняет пути к последним использованным файлам"""
    output_dir = Path(output_path).parent

    config_in_output_dir = str(output_dir / "project_documenter_config.json")

    latest_paths = {
        'config_path': config_in_output_dir,
        'output_path': output_path
    }

    print(f"Saving latest paths: {latest_paths}")

    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(LATEST_PATHS_FILE, 'w', encoding='utf-8') as f:
            json.dump(latest_paths, f, indent=2)

    except Exception as e:
        print(color_text(f"Error saving latest paths: {str(e)}", 'error'))


def load_latest_paths() -> Dict:
    """Загружает последние использованные пути из директории программы"""
    try:
        if os.path.exists(LATEST_PATHS_FILE):
            with open(LATEST_PATHS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(color_text(f"Error loading latest paths: {str(e)}", 'error'))
        return {}


def handle_ctrl_c(signum, frame):
    """Обработка нажатия Ctrl+C"""
    print(color_text("\n\nOperation cancelled by user", 'warning'))
    sys.exit(1)


signal.signal(signal.SIGINT, handle_ctrl_c)


def print_help(lang='en'):
    """Выводит информацию о доступных командах и флагах из JSON-файлов"""
    try:
        help_file = Path(__file__).parent / 'help_texts' / f'{lang}.json'
        if not help_file.exists():
            help_file = Path(__file__).parent / 'help_texts' / 'en.json'
        with open(help_file, 'r', encoding='utf-8') as f:
            texts = json.load(f)
        help_text = f"""
{color_text(texts['title'], 'highlight')}
{color_text(texts['usage'], 'info')}
    {PROGRAM_NAME} [command] [options]
{color_text(texts['commands'], 'info')}"""
        for cmd, desc in texts['commands_list']:
            help_text += f"\n    {color_text(cmd, 'path')}{' ' * (20 - len(cmd))}{desc}"
        help_text += f"\n\n{color_text(texts['examples'], 'info')}"
        for ex, desc in texts['examples_list']:
            help_text += f"\n    {ex}{' ' * (30 - len(ex))}{desc}"
        print(f"\n{help_text}\n")
    except Exception as e:
        print(color_text(f"\nError loading help: {str(e)}\n", 'error'))


def print_project_info():
    """Выводит информацию о проекте с цветным оформлением"""
    info_text = f"""
{color_text("Project Information:", 'info')}
{color_text("Author:", 'info')} {color_text("Anton Aleynichenko - https://aleynichenko.ru", 'highlight')}
{color_text("Repository:", 'info')} {color_text("https://github.com/Antongo22/OneFileProject", 'highlight')}
{color_text("Version:", 'info')} {color_text(VERSION, 'highlight')}
"""
    print(info_text)


def parse_args():
    """Разбирает аргументы командной строки с проверкой существования папки"""
    lang = 'en'
    project_path = None

    if len(sys.argv) > 1:
        if '-ru' in sys.argv:
            lang = 'ru'
            sys.argv.remove('-ru')
        elif '-en' in sys.argv:
            lang = 'en'
            sys.argv.remove('-en')

        if any(x in sys.argv[1:] for x in ("-h", "--help", "help", "помощь")):
            print_help(lang)
            sys.exit(0)
        elif "uninstall" in sys.argv[1:]:
            installer.uninstall()
            sys.exit(0)
        elif "update" in sys.argv[1:]:
            installer.update()
            sys.exit(0)
        elif "open" in sys.argv[1:]:
            open_output_file()
            sys.exit(0)
        elif "conf" in sys.argv[1:]:
            open_config_file()
            sys.exit(0)
        elif "reset" in sys.argv[1:]:
            handle_reset_command()
            sys.exit(0)
        elif "redo" in sys.argv[1:]:
            redo_documentation()
            sys.exit(0)
        elif "version" in sys.argv[1:]:
            print(f"Current version: {color_text(VERSION, 'highlight')}")
            sys.exit(0)
        elif "info" in sys.argv[1:]:
            print_project_info()
            sys.exit(0)
        elif "unpack" in sys.argv[1:]:
            if len(sys.argv) < 4:
                print(color_text("Error: unpack requires 2 arguments - the documentation file and the target folder",
                                 'error'))
                sys.exit(1)
            args = sys.argv[2:]
            doc_file = ' '.join(args[:-1]).strip('"\'')
            target_dir = args[-1].strip('"\'')
            unpack(doc_file, target_dir)
            sys.exit(0)
        elif "pwd" in sys.argv[1:]:
            print(color_text(f"Current working directory: {os.getcwd()}", 'info'))
            sys.exit(0)

        if len(sys.argv) > 1 and sys.argv[1] == ".":
            project_path = os.getcwd()
        elif len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            if sys.argv[1] not in ["unpack", "open", "conf", "reset", "redo", "update", "uninstall",
                                   "version", "info", "pwd"]:
                potential_path = sys.argv[1]
                if not os.path.exists(potential_path):
                    print(color_text(f"Error: Path '{potential_path}' does not exist!", 'error'))
                    sys.exit(1)
                if not os.path.isdir(potential_path):
                    print(color_text(f"Error: '{potential_path}' is not a directory!", 'error'))
                    sys.exit(1)
                project_path = os.path.abspath(potential_path)

    return project_path


def unpack(doc_file: str, target_dir: str):
    """Распаковывает проект из файла документации"""
    try:
        doc_path = Path(doc_file.strip('"\''))
        target_path = Path(target_dir.strip('"\''))

        if not doc_path.exists():
            print(color_text(f"Error: The documentation file '{doc_path}' was not found", 'error'))
            return False

        if target_path.exists() and any(target_path.iterdir()):
            print(color_text(f"Error: The target directory '{target_path}' is not empty", 'error'))
            return False

        target_path.mkdir(parents=True, exist_ok=True)

        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()

        structure_match = re.search(
            r'# (?:Структура проекта|Project Structure):.*?\n```.*?\n(.*?)\n```',
            content,
            re.DOTALL
        )

        if not structure_match:
            print(color_text("Error: The section with the project structure was not found.", 'error'))
            return False

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
                print(color_text(f"⚠️ Failed to create {rel_path} file: {str(e)}", 'warning'))

        print(color_text(f"✅ The project has been successfully unpacked in: {target_path}", 'success'))
        return True
    except Exception as e:
        print(color_text(f"❌ Unpacking error: {str(e)}", 'error'))
        return False


def open_output_file():
    """Открывает выходной файл в приложении по умолчанию"""
    config = load_config()
    output_path = None

    if config.get('output_path'):
        output_path = Path(config['output_path'])
        if not output_path.exists():
            output_path = None

    if output_path is None:
        latest_paths = load_latest_paths()
        if latest_paths.get('output_path'):
            output_path = Path(latest_paths['output_path'])
            if not output_path.exists():
                output_path = None

    if output_path is None:
        print(color_text("Error: Output file not found in config or latest paths", 'error'))
        return

    try:
        if sys.platform == 'win32':
            os.startfile(output_path)
        elif sys.platform == 'darwin':
            subprocess.run(['open', output_path])
        else:
            subprocess.run(['xdg-open', output_path])
        print(color_text(f"Opened output file: {output_path}", 'success'))
    except Exception as e:
        print(color_text(f"Error opening file: {str(e)}", 'error'))


def open_config_file():
    """Открывает файл конфигурации в приложении по умолчанию"""
    config_path = get_config_path()
    if not config_path.exists():
        latest_paths = load_latest_paths()
        if latest_paths.get('config_path'):
            config_path = Path(latest_paths['config_path'])
            if not config_path.exists():
                print(color_text("Error: Config file not found in standard or latest paths", 'error'))
                return

    try:
        if sys.platform == 'win32':
            os.startfile(config_path)
        elif sys.platform == 'darwin':
            subprocess.run(['open', config_path])
        else:
            subprocess.run(['xdg-open', config_path])
        print(color_text(f"Opened config file: {config_path}", 'success'))
    except Exception as e:
        print(color_text(f"Error opening config file: {str(e)}", 'error'))


def handle_reset_command():
    """Обрабатывает команду reset"""
    if len(sys.argv) > 2:
        if sys.argv[2] == '-c':
            reset_config()
        elif sys.argv[2] == '-o':
            reset_output()
        else:
            print(color_text("Invalid reset option. Use -c for config or -o for output", 'error'))
    else:
        reset_config()
        reset_output()


def reset_config():
    """Сбрасывает конфигурацию"""
    try:
        config_path = get_config_path()
        if config_path.exists():
            config_path.unlink()
            print(color_text("Config file has been reset", 'success'))
        else:
            print(color_text("Config file does not exist", 'warning'))
    except Exception as e:
        print(color_text(f"Error resetting config: {str(e)}", 'error'))


def reset_output():
    """Сбрасывает выходной файл"""
    config = load_config()
    if not config['output_path']:
        print(color_text("Output path is not set in config", 'warning'))
        return

    output_path = Path(config['output_path'])
    try:
        if output_path.exists():
            output_path.unlink()
            print(color_text(f"Output file {output_path} has been reset", 'success'))
        else:
            print(color_text(f"Output file {output_path} does not exist", 'warning'))
    except Exception as e:
        print(color_text(f"Error resetting output file: {str(e)}", 'error'))


def redo_documentation():
    """Повторно генерирует документацию"""
    config_path = get_config_path()
    if not config_path.exists():
        print(color_text("Error: Config file does not exist. Run the program without 'redo' first.", 'error'))
        return

    config = load_config()
    if not config['project_path']:
        print(color_text("Error: Project path is not set in config", 'error'))
        return

    try:
        root_path = os.path.normpath(config['project_path'])
        root_name = os.path.basename(root_path)

        print(color_text("\nScanning project structure...", 'info'))
        tree, files = generate_file_tree(root_path, config)

        print(color_text("\nGenerating documentation...", 'info'))
        md_content = (
            f"# Project Structure: {root_name}\n\n"
            f"```\n{root_name}/\n{tree}\n```\n\n"
            f"# Files Content\n\n{get_file_contents(files)}"
        )

        output_path = Path(config['output_path'])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        save_latest_paths(str(output_path))
        print(color_text("\nDocumentation regenerated successfully!", 'success'))
        print(color_text(f"Output file: {output_path}", 'path'))
        print(color_text(f"Total files processed: {len(files)}", 'info'))

    except Exception as e:
        print(color_text(f"\nError: {str(e)}", 'error'))


def color_text(text: str, color_type: str) -> str:
    """Возвращает цветной текст для консоли"""
    return f"{COLORS.get(color_type, '')}{text}{Style.RESET_ALL}"


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
    {PROGRAM_NAME.upper()} {VERSION}
    """
    print(color_text(header, 'highlight'))
    print(color_text("=" * 60, 'info') + "\n")


def get_config_path(config: Optional[Dict] = None) -> Path:
    """Возвращает путь к файлу конфигурации"""
    if config and config.get('project_path'):
        return Path(config['project_path']) / CONFIG_FILE
    return Path(CONFIG_FILE)


def load_config() -> Dict:
    """Загружает конфигурацию без рекурсии"""
    try:
        config_path = Path(CONFIG_FILE)
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if config.get('project_path'):
                    project_config_path = Path(config['project_path']) / CONFIG_FILE
                    if not project_config_path.exists():
                        project_config_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(project_config_path, 'w', encoding='utf-8') as pf:
                            json.dump(config, pf, indent=2)
                        config_path.unlink()
                return {**DEFAULT_CONFIG, **config}

        project_config_path = Path(DEFAULT_CONFIG['project_path']) / CONFIG_FILE if DEFAULT_CONFIG['project_path'] else None
        if project_config_path and project_config_path.exists():
            with open(project_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {**DEFAULT_CONFIG, **config}

        return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(color_text(f"Error loading config: {str(e)}", 'error'))
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict):
    """Сохраняет конфигурацию в файл"""
    try:
        if not config.get('project_path'):
            print(color_text("Cannot save config: project path is not set", 'error'))
            return

        output_file = Path(config['output_path']).name
        if output_file not in config['ignore_files']:
            config['ignore_files'].append(output_file)

        config_path = Path(config['project_path']) / CONFIG_FILE
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        print(color_text(f"Configuration saved successfully in {config_path}", 'success'))
    except Exception as e:
        print(color_text(f"Error saving config: {str(e)}", 'error'))


def get_input(prompt: str, default: Optional[str] = None) -> str:
    """Получает ввод от пользователя с цветными подсказками"""
    if default:
        prompt = color_text(f"{prompt} [{default}]: ", 'info')
    else:
        prompt = color_text(f"{prompt}: ", 'info')
    return input(prompt).strip() or default


def should_ignore(path: str, rel_path: str, config: Dict) -> bool:
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


def generate_file_tree(root_path: str, config: Dict, current_path: str = None, prefix: str = '') -> Tuple[
    str, List[Dict[str, str]]]:
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


def get_language(extension: str) -> str:
    """Определяет язык для подсветки синтаксиса"""
    return LANGUAGE_MAPPING.get(extension.lower(), 'text')


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


def get_file_contents(files_info: List[Dict[str, str]]) -> str:
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


def edit_config(config: Dict, cli_project_path: str = None) -> Dict:
    """Интерактивное редактирование конфигурации"""
    if cli_project_path:
        project_path = os.path.abspath(cli_project_path)
        config['project_path'] = project_path
        if config['output_path'] == DEFAULT_CONFIG['output_path']:
            config['output_path'] = str(Path(project_path) / "project_documentation.md")
        return config

    print(color_text("\nCurrent configuration:", 'highlight'))
    print(json.dumps(config, indent=2))

    print(color_text("\nEdit configuration:", 'highlight'))
    config['project_path'] = get_input("Project path", config['project_path'])

    if config['project_path'] and config['output_path'] == DEFAULT_CONFIG['output_path']:
        config['output_path'] = str(Path(config['project_path']) / "project_documentation.md")

    config['output_path'] = get_input("Output file path", config['output_path'])

    print(color_text("\nFilter settings:", 'highlight'))
    config['show_hidden'] = input(color_text("Show hidden files? (y/n) [n]: ", 'info')).lower() == 'y'

    print(color_text("\nWhitelist settings:", 'highlight'))
    print(color_text("Current whitelist paths (empty means all files):", 'info'),
          ', '.join(config.get('whitelist_paths', [])))
    if input(color_text("Edit? (y/n) [n]: ", 'info')).lower() == 'y':
        new_paths = input(
            color_text("Enter paths to include (comma separated, * for wildcard, relative to project): ", 'info'))
        config['whitelist_paths'] = [p.strip() for p in new_paths.split(',') if p.strip()]

    print(color_text("\nIgnore settings:", 'highlight'))
    print(color_text("Current ignored folders:", 'info'), ', '.join(config['ignore_folders']))
    if input(color_text("Edit? (y/n) [n]: ", 'info')).lower() == 'y':
        new_folders = input(color_text("Enter folders to ignore (comma separated): ", 'info'))
        config['ignore_folders'] = [f.strip() for f in new_folders.split(',') if f.strip()] or config['ignore_folders']

    print(color_text("\nCurrent ignored files:", 'info'), ', '.join(config['ignore_files']))
    if input(color_text("Edit? (y/n) [n]: ", 'info')).lower() == 'y':
        new_files = input(color_text("Enter file patterns to ignore (comma separated, * for wildcard): ", 'info'))
        config['ignore_files'] = [f.strip() for f in new_files.split(',') if f.strip()] or config['ignore_files']

    print(color_text("\nCurrent ignored paths:", 'info'), ', '.join(config['ignore_paths']))
    if input(color_text("Edit? (y/n) [n]: ", 'info')).lower() == 'y':
        new_paths = input(color_text("Enter full paths to ignore (comma separated, * for wildcard): ", 'info'))
        config['ignore_paths'] = [p.strip() for p in new_paths.split(',') if p.strip()] or config['ignore_paths']

    return config


def main():

    cli_project_path = parse_args()
    print_header()

    config = load_config()
    config = edit_config(config, cli_project_path)

    if not config['project_path']:
        print(color_text("Error: Project path is required!", 'error'))
        return

    if not os.path.isdir(config['project_path']):
        print(color_text(f"Error: Directory '{config['project_path']}' does not exist!", 'error'))
        return

    try:
        root_path = os.path.normpath(config['project_path'])
        root_name = os.path.basename(root_path)

        print(color_text("\nScanning project structure...", 'info'))
        tree, files = generate_file_tree(root_path, config)

        print(color_text("\nGenerating documentation...", 'info'))
        md_content = (
            f"# Project Structure: {root_name}\n\n"
            f"```\n{root_name}/\n{tree}\n```\n\n"
            f"# Files Content\n\n{get_file_contents(files)}"
        )

        output_path = Path(config['output_path'])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        save_config(config)
        save_latest_paths(str(output_path))

        print(color_text("\nDocumentation generated successfully!", 'success'))
        print(color_text(f"Output file: {output_path}", 'path'))
        print(color_text(f"Total files processed: {len(files)}", 'info'))

    except Exception as e:
        print(color_text(f"\nError: {str(e)}", 'error'))


if __name__ == "__main__":
    main()