import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import fnmatch
from colorama import init, Fore, Style

import installer

init(autoreset=True)

PROGRAM_NAME = "ofp"
CONFIG_FILE = "project_documenter_config.json"

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
    'output_path': 'documentation.md',
    'ignore_folders': ['.git', '__pycache__', 'node_modules', 'venv'],
    'ignore_files': ['.gitignore', '.env', '*.pyc'],
    'ignore_paths': [],
    'show_hidden': False
}


def parse_args():
    """Разбирает аргументы командной строки"""
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        installer.uninstall()
        sys.exit(0)

    project_path = os.getcwd() if len(sys.argv) > 1 and sys.argv[1] == "." else None

    return project_path


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
    {PROGRAM_NAME.upper()} v1.0
    """
    print(color_text(header, 'highlight'))
    print(color_text("=" * 60, 'info') + "\n")


def load_config() -> Dict:
    """Загружает конфигурацию из файла"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                merged_config = {**DEFAULT_CONFIG, **config}

                if 'ignore_paths' not in merged_config:
                    merged_config['ignore_paths'] = []

                return merged_config
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(color_text(f"Error loading config: {str(e)}", 'error'))
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict):
    """Сохраняет конфигурацию в файл"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        print(color_text("Configuration saved successfully", 'success'))
    except Exception as e:
        print(color_text(f"Error saving config: {str(e)}", 'error'))


def get_input(prompt: str, default: Optional[str] = None) -> str:
    """Получает ввод от пользователя с цветными подсказками"""
    if default:
        prompt = color_text(f"{prompt} [{default}]: ", 'info')
    else:
        prompt = color_text(f"{prompt}: ", 'info')

    user_input = input(prompt).strip()
    return user_input if user_input else default


def should_ignore(path: str, rel_path: str, config: Dict) -> bool:
    """Проверяет нужно ли игнорировать файл/папку"""
    name = os.path.basename(path)
    rel_path = rel_path.replace('\\', '/')

    if not config['show_hidden'] and name.startswith('.'):
        return True

    for ignore_path in config['ignore_paths']:
        if fnmatch.fnmatch(rel_path, ignore_path):
            return True

    if os.path.isdir(path):
        return any(ignore in rel_path.split('/') for ignore in config['ignore_folders'])

    return any(fnmatch.fnmatch(name, pattern) for pattern in config['ignore_files'])


def generate_file_tree(root_path: str, config: Dict, current_path: str = None, prefix: str = '') -> Tuple[
    str, List[Dict[str, str]]]:
    """Генерирует дерево файлов (чистый текст для файла)"""
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
            subtree, sub_files = generate_file_tree(
                root_path, config, full_path,
                prefix + ('│   ' if pointer == '├── ' else '    ')
            )
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
    """Получает содержимое файлов (чистый текст для файла)"""
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
        config['project_path'] = cli_project_path
        config['output_path'] = str(Path(cli_project_path).parent / "project_documentation.md")
        return config

    print(color_text("\nCurrent configuration:", 'highlight'))
    print(json.dumps(config, indent=2))

    print(color_text("\nEdit configuration:", 'highlight'))
    config['project_path'] = get_input("Project path", config['project_path'])
    config['output_path'] = get_input("Output file path", config['output_path'])

    print(color_text("\nFilter settings:", 'highlight'))
    config['show_hidden'] = input(color_text("Show hidden files? (y/n) [n]: ", 'info')).lower() == 'y'

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

        print(color_text("\nDocumentation generated successfully!", 'success'))
        print(color_text(f"Output file: {output_path}", 'path'))
        print(color_text(f"Total files processed: {len(files)}", 'info'))

    except Exception as e:
        print(color_text(f"\nError: {str(e)}", 'error'))


if __name__ == "__main__":
    main()