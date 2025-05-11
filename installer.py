import os
import sys
import shutil
import subprocess
import stat
from pathlib import Path


PROGRAM_NAME = "ofp"
PROGRAM_FILES_DIR = "OFP_Documenter"
REPO_URL = "https://github.com/Antongo22/OneFileProject"
DEFAULT_VERSION = "0.0.0"


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


def install_dependencies(install_dir):
    """Устанавливает зависимости из requirements.txt"""
    requirements = install_dir / "requirements.txt"
    if not requirements.exists():
        print("⚠️ requirements.txt not found, skipping dependencies installation")
        return

    print("🔄 Installing dependencies from requirements.txt...")
    try:
        if sys.platform == "win32":
            python_exec = sys.executable
        else:
            python_exec = "python3"

        # Установка базовых зависимостей без импортов
        required_packages = ["colorama", "textual", "typing"]
        print("📦 Installing core dependencies...")
        for pkg in required_packages:
            try:
                subprocess.run(
                    [python_exec, "-m", "pip", "install", pkg],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except Exception as e:
                print(f"⚠️ Warning: Couldn't install {pkg}: {str(e)}")

        # Теперь устанавливаем все остальные зависимости
        subprocess.run(
            [python_exec, "-m", "pip", "install", "-r", str(requirements)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e.stderr.decode().strip()}")
    except Exception as e:
        print(f"❌ Error installing dependencies: {str(e)}")


def get_current_version(install_dir):
    """Получает текущую версию программы без импорта модулей"""
    try:
        version_file = install_dir / "data/version"
        if version_file.exists():
            with open(version_file, 'r') as f:
                return f.read().strip()
    except Exception:
        pass
    return DEFAULT_VERSION


def update():
    """Обновляет программу через git pull с выводом информации о версиях"""
    temp_dir = None
    try:
        install_dir = get_install_dir()
        
        if not install_dir.exists():
            print("❌ Program not installed. Please run installation first.")
            return
            
        current_version = get_current_version(install_dir)

        temp_dir = install_dir.parent / f"{PROGRAM_FILES_DIR}_temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir, onerror=handle_remove_readonly)

        print(f"🔄 Cloning repository for update (current version: {current_version})...")
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

        shutil.rmtree(install_dir, onerror=handle_remove_readonly)
        shutil.move(temp_dir, install_dir)

        install_dependencies(install_dir)

        print(f"✅ Successfully updated from version {current_version} to {new_version}!")

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


def install():
    """Устанавливает программу в пользовательскую директорию"""
    try:
        install_dir = get_install_dir()

        install_dir.mkdir(parents=True, exist_ok=True)
        print(f"🔄 Installing the program in: {install_dir}")

        current_dir = Path(__file__).parent.resolve()
        for item in current_dir.iterdir():
            if item.name not in ['.git', '__pycache__', '.venv', ".idea"]:
                dest = install_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)

        install_dependencies(install_dir)

        if sys.platform == "win32":
            bin_path = Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps"
            bin_path.mkdir(exist_ok=True)
            target_path = bin_path / f"{PROGRAM_NAME}.bat"
            bat_content = f'@python "{install_dir / "main.py"}" %*'
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
        else:
            # Улучшенная установка для Linux
            bin_path = Path.home() / ".local" / "bin"
            bin_path.mkdir(exist_ok=True)
            target_path = bin_path / PROGRAM_NAME

            # Создаем исполняемый файл с улучшенной поддержкой нахождения пути к Python
            with open(target_path, 'w') as f:
                f.write(f"""#!/bin/bash
# Find Python even if the path is not in environment variables
PYTHON_PATH="$(which python3 2>/dev/null || which python 2>/dev/null)"

if [ -z "$PYTHON_PATH" ]; then
    # Check typical Python installation locations
    for path in /usr/bin/python3 /usr/local/bin/python3 /usr/bin/python /usr/local/bin/python; do
        if [ -x "$path" ]; then
            PYTHON_PATH="$path"
            break
        fi
    done

    # If still not found, display error
    if [ -z "$PYTHON_PATH" ]; then
        echo "Error: Python not found. Please install Python 3."
        exit 1
    fi
fi

# Run the program with the found Python
"$PYTHON_PATH" "{install_dir / 'main.py'}" "$@"
""")

            os.chmod(target_path, 0o755)
            
            # Также создаем ссылку в /usr/local/bin, если это возможно (требует sudo)
            try:
                print("\nTrying to create a system link (may require password)...")
                system_bin = Path("/usr/local/bin") / PROGRAM_NAME
                subprocess.run(["sudo", "ln", "-sf", str(target_path), str(system_bin)])
                print(f"✅ System link created: {system_bin}")
            except Exception as e:
                print(f"ℹ️ Could not create system link (this is not an error): {str(e)}")

        print(f"\n✅ The installation is complete! Now use the command '{PROGRAM_NAME}'")

        if sys.platform == "win32":
            print("\n⚠️ For a team to work from anywhere:")
            print(f"1. Press Win+R, type 'sysdm.cpl' and press Enter")
            print("2. Go to the 'Advanced' tab")
            print("3. Click on 'Environment Variables'")
            print(f"4. In the 'System Variables' section, find the 'Path' and click 'Edit'")
            print(f"5. Add a new path: {bin_path}")
        else:
            # Проверяем, добавлен ли путь в PATH
            path_str = os.environ.get('PATH', '')
            if str(bin_path) not in path_str:
                print("\n⚠️ To make the command work from anywhere, add to your ~/.bashrc or ~/.zshrc:")
                print(f'export PATH="$PATH:{bin_path}"')
                print("And run: source ~/.bashrc")
                
                # Автоматически добавляем путь в .bashrc, если файл существует
                bashrc_path = Path.home() / ".bashrc"
                if bashrc_path.exists():
                    try:
                        # Проверяем, не добавлена ли уже эта строка
                        with open(bashrc_path, 'r') as f:
                            content = f.read()
                        
                        if f'export PATH="$PATH:{bin_path}"' not in content:
                            with open(bashrc_path, 'a') as f:
                                f.write(f'\n# Added automatically by {PROGRAM_NAME} installer\nexport PATH="$PATH:{bin_path}"\n')
                            print(f"✅ Path automatically added to {bashrc_path}")
                            print("Run this command to activate changes:")
                            print(f"source {bashrc_path}")
                    except Exception as e:
                        print(f"ℹ️ Failed to automatically update .bashrc: {str(e)}")
                
                # То же самое для .zshrc, если пользователь использует zsh
                zshrc_path = Path.home() / ".zshrc"
                if zshrc_path.exists():
                    try:
                        with open(zshrc_path, 'r') as f:
                            content = f.read()
                        
                        if f'export PATH="$PATH:{bin_path}"' not in content:
                            with open(zshrc_path, 'a') as f:
                                f.write(f'\n# Added automatically by {PROGRAM_NAME} installer\nexport PATH="$PATH:{bin_path}"\n')
                            print(f"✅ Path automatically added to {zshrc_path}")
                            print("Run this command to activate changes:")
                            print(f"source {zshrc_path}")
                    except Exception as e:
                        print(f"ℹ️ Failed to automatically update .zshrc: {str(e)}")

    except Exception as e:
        print(f"\n❌ Installation error: {e}")
        sys.exit(1)





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
