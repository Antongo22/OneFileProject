import os
import sys
from pathlib import Path
from colorama import init
import signal
import program.config_utils as cfg
import installer
import program.utils as utils
import program.commands as commands
from program.tui import run_tui
from program.translator import translator

init(autoreset=True)

translator.set_language(utils.load_latest_config().get('language', 'en'))


def handle_ctrl_c(signum, frame):
    """Обработка нажатия Ctrl+C"""
    print(utils.color_text("\n\nOperation cancelled by user", 'warning'))
    sys.exit(1)


signal.signal(signal.SIGINT, handle_ctrl_c)



def parse_args():
    """Разбирает аргументы командной строки с проверкой существования папки"""
    lang = utils.load_latest_config().get('language', 'en')
    project_path = None

    if len(sys.argv) > 1:
        if '-ru' in sys.argv:
            lang = 'ru'
            sys.argv.remove('-ru')
        elif '-en' in sys.argv:
            lang = 'en'
            sys.argv.remove('-en')

        if any(x in sys.argv[1:] for x in ("-h", "--help", "help", "помощь")):
            commands.print_help(lang)
            sys.exit(0)
        elif "uninstall" in sys.argv[1:]:
            installer.uninstall()
            sys.exit(0)
        elif "update" in sys.argv[1:]:
            print(utils.color_text("❗️ The entire cache will be cleared!", 'warning'))
            installer.update()
            sys.exit(0)
        elif "open" in sys.argv[1:]:
            commands.open_output_file()
            sys.exit(0)
        elif "conf" in sys.argv[1:]:
            commands.open_config_file()
            sys.exit(0)
        elif "reset" in sys.argv[1:]:
            commands.handle_reset_command()
            sys.exit(0)
        elif "redo" in sys.argv[1:]:
            commands.redo_documentation()
            sys.exit(0)
        elif "version" in sys.argv[1:]:
            print(f"Current version: {utils.color_text(cfg.VERSION, 'highlight')}")
            sys.exit(0)
        elif "info" in sys.argv[1:]:
            print(commands.print_project_info())
            sys.exit(0)
        elif "unpack" in sys.argv[1:]:
            if len(sys.argv) < 4:
                print(utils.color_text("Error: unpack requires 2 arguments - the documentation file and the target folder",
                                 'error'))
                sys.exit(1)
            args = sys.argv[2:]
            doc_file = ' '.join(args[:-1]).strip('"\'')
            target_dir = args[-1].strip('"\'')
            sec, text = commands.unpack(doc_file, target_dir)
            print(text)
            sys.exit(0)
        elif "pwd" in sys.argv[1:]:

            print(utils.color_text(f"Current working directory: {Path(__file__).parent}", 'info'))
            sys.exit(0)
        elif "tui" in sys.argv[1:]:
            run_tui()
            sys.exit(0)
        elif "lang" in sys.argv[1:]:
            if len(sys.argv) > 2 and sys.argv[2] in ['en', 'ru']:
                success, message = commands.change_language(sys.argv[2])
                print(utils.color_text(message, 'success' if success else 'error'))
            elif len(sys.argv) == 2:
                print(utils.color_text(f"Current language: {lang}", 'info'))
            else:
                print(utils.color_text("Usage: ofp lang [en|ru]", 'error'))
            sys.exit(0)

        if len(sys.argv) > 1 and sys.argv[1] == ".":
            project_path = os.getcwd()
        elif len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            if sys.argv[1] not in ["unpack", "open", "conf", "reset", "redo", "update", "uninstall",
                                   "version", "info", "pwd", "tui", "lang"]:
                potential_path = sys.argv[1]
                if not os.path.exists(potential_path):
                    print(utils.color_text(f"Error: Path '{potential_path}' does not exist!", 'error'))
                    sys.exit(1)
                if not os.path.isdir(potential_path):
                    print(utils.color_text(f"Error: '{potential_path}' is not a directory!", 'error'))
                    sys.exit(1)
                project_path = os.path.abspath(potential_path)

    return project_path






def main():
    cli_project_path = parse_args()
    commands.print_header()

    config = utils.load_config()
    config = utils.edit_config(config, cli_project_path)

    project_path = config.get('project_path', '')
    output_path = config.get('output_path', 'project_documentation.md')

    result = commands.generate_documentation(project_path, output_path, config)
    print(result)

if __name__ == "__main__":
    main()