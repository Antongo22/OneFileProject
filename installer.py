import os
import sys
import shutil
import subprocess
import stat
from pathlib import Path

import main

PROGRAM_NAME = "ofp"
PROGRAM_FILES_DIR = "OFP_Documenter"
REPO_URL = "https://github.com/Antongo22/OneFileProject"


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

def update():
    """Обновляет программу через git pull с выводом информации о версиях"""
    temp_dir = None
    try:
        install_dir = get_install_dir()
        current_version = main.VERSION

        if not install_dir.exists():
            print("❌ Программа не установлена. Сначала выполните установку.")
            return

        temp_dir = install_dir.parent / f"{PROGRAM_FILES_DIR}_temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir, onerror=handle_remove_readonly)

        print(f"🔄 Клонируем репозиторий для обновления (текущая версия: {current_version})...")
        subprocess.run(["git", "clone", REPO_URL, temp_dir], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        version_file = temp_dir / "version"
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

        print(f"✅ Программа успешно обновлена с {current_version} на {new_version}!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при выполнении git: {e.stderr.decode().strip()}")
    except Exception as e:
        print(f"❌ Ошибка обновления: {str(e)}")
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

        if install_dir.exists():
            shutil.rmtree(install_dir, onerror=handle_remove_readonly)

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
            bin_path = Path(os.environ.get('APPDATA',
                                           'C:\\Users\\%USERNAME%\\AppData\\Roaming')) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            bin_path.mkdir(parents=True, exist_ok=True)

            bat_path = bin_path / f"{PROGRAM_NAME}.bat"
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(f'@echo off\npython "{install_dir / "main.py"}" %*')

            os.environ['PATH'] += f";{bin_path}"
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
            print("\n⚠️ Для работы команды из любого места:")
            print(f"1. Нажмите Win+R, введите 'sysdm.cpl' и нажмите Enter")
            print("2. Перейдите на вкладку 'Дополнительно'")
            print("3. Нажмите 'Переменные среды'")
            print(f"4. В разделе 'Системные переменные' найдите 'Path' и нажмите 'Изменить'")
            print(f"5. Добавьте новый путь: {bin_path}")
        else:
            path_str = os.environ.get('PATH', '')
            if str(bin_path) not in path_str:
                print("\n⚠️ Добавьте в ~/.bashrc или ~/.zshrc:")
                print(f'export PATH="$PATH:{bin_path}"')
                print("И выполните: source ~/.bashrc")

    except Exception as e:
        print(f"\n❌ Ошибка установки: {str(e)}")
        sys.exit(1)


def uninstall():
    """Полностью удаляет программу"""
    try:
        install_dir = get_install_dir()

        if install_dir.exists():
            shutil.rmtree(install_dir, onerror=handle_remove_readonly)
            print(f"✅ Удалена директория: {install_dir}")

        if sys.platform == "win32":
            bin_path = Path(os.environ.get('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            target_path = bin_path / f"{PROGRAM_NAME}.bat"
        else:
            bin_path = Path.home() / ".local" / "bin"
            target_path = bin_path / PROGRAM_NAME

        if target_path.exists():
            target_path.unlink(missing_ok=True)
            print(f"✅ Удалена команда: {PROGRAM_NAME}")

    except Exception as e:
        print(f"❌ Ошибка удаления: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "uninstall":
            uninstall()
        elif sys.argv[1] == "update":
            update()
        else:
            print("❌ Неизвестная команда. Доступные команды: install, uninstall, update")
    else:
        install()