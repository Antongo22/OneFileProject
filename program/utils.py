import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Tuple, Optional
import fnmatch
from colorama import init, Fore, Style
import signal
import re
import program.config_utils as cfg
import installer

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
