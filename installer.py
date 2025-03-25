import os
import sys
import shutil
from pathlib import Path

PROGRAM_NAME = "ofp"
PROGRAM_FILES_DIR = "OFP_Documenter"


def get_install_dir():
    """Возвращает путь для установки программы (без прав админа)"""
    if sys.platform == "win32":
        return Path(os.environ.get('LOCALAPPDATA', 'C:\\Users\\%USERNAME%\\AppData\\Local')) / PROGRAM_FILES_DIR
    else:
        return Path.home() / ".local" / "lib" / PROGRAM_FILES_DIR.lower()


def install():
    """Устанавливает программу в пользовательскую директорию"""
    try:
        install_dir = get_install_dir()

        install_dir.mkdir(parents=True, exist_ok=True)
        print(f"🔄 Устанавливаю программу в: {install_dir}")

        current_dir = Path(__file__).parent.resolve()
        for item in current_dir.iterdir():
            if item.name not in ['.git', '__pycache__', 'venv']:
                dest = install_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)

        if sys.platform == "win32":
            bin_path = Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps"
            bin_path.mkdir(exist_ok=True)
            target_path = bin_path / f"{PROGRAM_NAME}.bat"
            bat_content = f'@python "{install_dir / "main.py"}" %*'
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
        else:
            bin_path = Path.home() / ".local" / "bin"
            bin_path.mkdir(exist_ok=True)
            target_path = bin_path / PROGRAM_NAME
            if target_path.exists():
                target_path.unlink()
            os.symlink(install_dir / "main.py", target_path)
            os.chmod(install_dir / "main.py", 0o755)

        print(f"\n✅ Установка завершена! Теперь используйте команду '{PROGRAM_NAME}'")

        if sys.platform == "win32":
            print(f"\nЕсли команда '{PROGRAM_NAME}' не работает, добавьте в PATH:")
            print(bin_path)
        else:
            path_str = os.environ.get('PATH', '')
            if str(bin_path) not in path_str:
                print(f"\n⚠️ Добавьте в ~/.bashrc или ~/.zshrc:")
                print(f'export PATH="$PATH:{bin_path}"')
                print("И выполните: source ~/.bashrc")

    except Exception as e:
        print(f"\n❌ Ошибка установки: {e}")
        sys.exit(1)


def uninstall():
    """Полностью удаляет программу"""
    try:
        install_dir = get_install_dir()

        if install_dir.exists():
            shutil.rmtree(install_dir)
            print(f"✅ Удалена директория: {install_dir}")

        if sys.platform == "win32":
            target_path = Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps" / f"{PROGRAM_NAME}.bat"
        else:
            target_path = Path.home() / ".local" / "bin" / PROGRAM_NAME

        if target_path.exists():
            target_path.unlink()
            print(f"✅ Удалена команда: {PROGRAM_NAME}")

    except Exception as e:
        print(f"❌ Ошибка удаления: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall()
    else:
        install()