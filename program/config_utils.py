from pathlib import Path
from colorama import init, Fore, Style

PREFIX = "../data"

# Создаем папку, если она не существует
Path(PREFIX).mkdir(parents=True, exist_ok=True)

PROGRAM_NAME = "ofp"
CONFIG_FILE = "project_documenter_config.json"
LATEST_PATHS_FILE = str(Path(__file__).parent / f"{PREFIX}/latest_paths.json")

def get_version():
    """Получает версию из файла version или возвращает v0.0.0 при ошибке"""
    try:
        with open(Path(__file__).parent / f'{PREFIX}/version', 'r') as f:
            print(f)
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
