import os
import json
from pathlib import Path
from typing import Tuple, Optional
import fnmatch
from colorama import init, Style
import program.config_utils as cfg

init(autoreset=True)



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

        with open(cfg.LATEST_PATHS_FILE, 'w', encoding='utf-8') as f:
            json.dump(latest_paths, f, indent=2)

    except Exception as e:
        print(color_text(f"Error saving latest paths: {str(e)}", 'error'))


def load_latest_paths() -> dict:
    """Загружает последние использованные пути из директории программы"""
    try:
        if os.path.exists(cfg.LATEST_PATHS_FILE):
            with open(cfg.LATEST_PATHS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(color_text(f"Error loading latest paths: {str(e)}", 'error'))
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
        print(color_text(f"Error loading config: {str(e)}", 'error'))
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
            print(color_text("Cannot save config: project path is not set", 'error'))
            return

        output_file = Path(config['output_path']).name
        if output_file not in config['ignore_files']:
            config['ignore_files'].append(output_file)

        config_path = Path(config['project_path']) / cfg.CONFIG_FILE
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

    print(color_text("\nCurrent configuration:", 'highlight'))
    print(json.dumps(config, indent=2))

    print(color_text("\nEdit configuration:", 'highlight'))
    config['project_path'] = get_input("Project path", config['project_path'])

    if config['project_path'] and config['output_path'] == cfg.DEFAULT_CONFIG['output_path']:
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
