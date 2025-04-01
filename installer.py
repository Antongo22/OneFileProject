import os
import sys
import shutil
import subprocess
import stat
from pathlib import Path
import program.config_utils as cfg

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


def setup_venv(install_dir):
    """Создает виртуальное окружение и устанавливает зависимости"""
    venv_path = install_dir / "venv"
    print("🔄 Creating virtual environment...")

    try:
        # Создаем venv без наследования системных пакетов
        subprocess.run([sys.executable, "-m", "venv", "--clear", str(venv_path)],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to create venv: {e.stderr.decode().strip()}")

    # Определяем правильный способ запуска pip
    if sys.platform == "win32":
        python_bin = venv_path / "Scripts" / "python.exe"
        # В Windows используем python -m pip вместо прямого вызова pip
        pip_command = [str(python_bin), "-m", "pip"]
    else:
        python_bin = venv_path / "bin" / "python"
        pip_command = [str(python_bin), "-m", "pip"]

    # Обновляем pip (новый способ)
    try:
        subprocess.run([*pip_command, "install", "--upgrade", "pip"],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Pip upgrade warning: {e.stderr.decode().strip()}")
        # Не прерываем установку из-за ошибки обновления pip

    # Устанавливаем зависимости
    requirements = install_dir / "requirements.txt"
    if requirements.exists():
        print("🔄 Installing dependencies...")
        try:
            subprocess.run([*pip_command, "install", "-r", str(requirements)],
                           check=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to install dependencies: {e.stderr.decode().strip()}")
    else:
        print("⚠️ requirements.txt not found, skipping dependencies installation")

    return python_bin



def install():
    """Устанавливает программу в пользовательскую директорию с виртуальным окружением"""
    try:
        install_dir = get_install_dir()

        install_dir.mkdir(parents=True, exist_ok=True)
        print(f"🔄 Installing the program in: {install_dir}")

        current_dir = Path(__file__).parent.resolve()
        for item in current_dir.iterdir():
            if item.name not in ['.git', '__pycache__', '.venv', ".idea", "venv"]:
                dest = install_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)

        python_bin = setup_venv(install_dir)

        if sys.platform == "win32":
            bin_path = Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps"
            bin_path.mkdir(exist_ok=True)
            target_path = bin_path / f"{PROGRAM_NAME}.bat"
            bat_content = f'@"{python_bin}" "{install_dir / "main.py"}" %*'
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
        else:
            bin_path = Path.home() / ".local" / "bin"
            bin_path.mkdir(exist_ok=True)
            target_path = bin_path / PROGRAM_NAME
            if target_path.exists():
                target_path.unlink()

            script_content = f'''#!/bin/bash
source "{install_dir / "venv/bin/activate"}"
python "{install_dir / "main.py"}" "$@"
'''
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            os.chmod(target_path, 0o755)

        print(f"\n✅ The installation is complete! Now use the command '{PROGRAM_NAME}'")

        if sys.platform == "win32":
            print("\n⚠️ For a team to work from anywhere:")
            print(f"1. Press Win+R, type 'sysdm.cpl' and press Enter")
            print("2. Go to the 'Advanced' tab")
            print("3. Click on 'Environment Variables'")
            print(f"4. In the 'System Variables' section, find the 'Path' and click 'Edit'")
            print(f"5. Add a new path: {bin_path}")
        else:
            path_str = os.environ.get('PATH', '')
            if str(bin_path) not in path_str:
                print("\n⚠️ Add it to ~/.bashrc or ~/.zshrc:")
                print(f'export PATH="$PATH:{bin_path}"')
                print("And run: source ~/.bashrc")

    except Exception as e:
        print(f"\n❌ Installation error: {e}")
        sys.exit(1)


def update():
    """Обновляет программу через git pull с пересозданием виртуального окружения"""
    temp_dir = None
    try:
        install_dir = get_install_dir()
        current_version = cfg.VERSION

        if not install_dir.exists():
            print("❌ The program is not installed. First, perform the installation.")
            return

        temp_dir = install_dir.parent / f"{PROGRAM_FILES_DIR}_temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir, onerror=handle_remove_readonly)

        print(f"🔄 Cloning the repository for updating (current version: {current_version})...")
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

        # Удаляем старый venv если существует
        venv_path = install_dir / "venv"
        if venv_path.exists():
            shutil.rmtree(venv_path, onerror=handle_remove_readonly)

        shutil.rmtree(install_dir, onerror=handle_remove_readonly)
        shutil.move(temp_dir, install_dir)

        # Пересоздаем виртуальное окружение
        setup_venv(install_dir)

        print(f"✅ The program has been successfully updated from {current_version} to {new_version}!")

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