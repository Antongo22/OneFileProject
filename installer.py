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
    """Создает или пересоздает виртуальное окружение и устанавливает зависимости"""
    venv_path = install_dir / "venv"

    if venv_path.exists():
        print("🔄 Removing old virtual environment...")
        shutil.rmtree(venv_path, onerror=handle_remove_readonly)

    print("🔄 Creating new virtual environment...")

    try:
        subprocess.run([sys.executable, "-m", "venv", "--clear", str(venv_path)],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to create venv: {e.stderr.decode().strip()}")

    if sys.platform == "win32":
        python_bin = venv_path / "Scripts" / "python.exe"
        pip_cmd = [str(python_bin), "-m", "pip"]
    else:
        python_bin = venv_path / "bin" / "python"
        pip_cmd = [str(python_bin), "-m", "pip"]

    try:
        print("🔄 Updating pip...")
        subprocess.run([*pip_cmd, "install", "--upgrade", "pip"],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Pip upgrade warning: {e.stderr.decode().strip()}")

    requirements = install_dir / "requirements.txt"
    if requirements.exists():
        print("🔄 Installing dependencies...")
        try:
            subprocess.run([*pip_cmd, "install", "-r", str(requirements)],
                           check=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to install dependencies: {e.stderr.decode().strip()}")
    else:
        print("⚠️ requirements.txt not found, skipping dependencies installation")

    return python_bin


def install():
    """Устанавливает программу с созданием виртуального окружения"""
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
exec python "{install_dir / "main.py"}" "$@"
'''
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            os.chmod(target_path, 0o755)

        print(f"\n✅ Installation complete! Use command: '{PROGRAM_NAME}'")

    except Exception as e:
        print(f"\n❌ Installation error: {e}")
        sys.exit(1)


def update():
    """Обновляет программу с обязательным пересозданием venv"""
    temp_dir = None
    try:
        install_dir = get_install_dir()
        current_version = cfg.VERSION

        if not install_dir.exists():
            print("❌ Program not installed. Please install first.")
            return

        temp_dir = install_dir.parent / f"{PROGRAM_FILES_DIR}_temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir, onerror=handle_remove_readonly)

        print(f"🔄 Cloning repository (current version: {current_version})...")
        subprocess.run(["git", "clone", REPO_URL, temp_dir],
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

        version_file = temp_dir / "data/version"
        new_version = "unknown"
        if version_file.exists():
            with open(version_file, 'r') as f:
                new_version = f.read().strip()

        git_dir = temp_dir / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir, onerror=handle_remove_readonly)

        shutil.rmtree(install_dir, onerror=handle_remove_readonly)

        shutil.move(temp_dir, install_dir)

        print("🔄 Recreating virtual environment...")
        setup_venv(install_dir)

        print(f"✅ Successfully updated from {current_version} to {new_version}!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e.stderr.decode().strip()}")
    except Exception as e:
        print(f"❌ Update error: {str(e)}")
    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def uninstall():
    """Полностью удаляет программу"""
    try:
        install_dir = get_install_dir()

        if install_dir.exists():
            shutil.rmtree(install_dir, onerror=handle_remove_readonly)
            print(f"✅ Deleted directory: {install_dir}")

        if sys.platform == "win32":
            target_path = Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps" / f"{PROGRAM_NAME}.bat"
        else:
            target_path = Path.home() / ".local" / "bin" / PROGRAM_NAME

        if target_path.exists():
            target_path.unlink()
            print(f"✅ Removed command: {PROGRAM_NAME}")

    except Exception as e:
        print(f"❌ Uninstall error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "uninstall":
            uninstall()
        elif sys.argv[1] == "update":
            update()
        else:
            print("❌ Unknown command. Available: install, uninstall, update")
    else:
        install()