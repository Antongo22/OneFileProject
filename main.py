import os
import sys
from pathlib import Path
from colorama import init
import signal
import program.config_utils as cfg
import installer
import program.utils as utils
import program.commands as commands

init(autoreset=True)




def handle_ctrl_c(signum, frame):
    """Обработка нажатия Ctrl+C"""
    print(utils.color_text("\n\nOperation cancelled by user", 'warning'))
    sys.exit(1)


signal.signal(signal.SIGINT, handle_ctrl_c)



def parse_args():
    """Разбирает аргументы командной строки с проверкой существования папки"""
    lang = 'en'
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
            commands.print_project_info()
            sys.exit(0)
        elif "unpack" in sys.argv[1:]:
            if len(sys.argv) < 4:
                print(utils.color_text("Error: unpack requires 2 arguments - the documentation file and the target folder",
                                 'error'))
                sys.exit(1)
            args = sys.argv[2:]
            doc_file = ' '.join(args[:-1]).strip('"\'')
            target_dir = args[-1].strip('"\'')
            commands.unpack(doc_file, target_dir)
            sys.exit(0)
        elif "pwd" in sys.argv[1:]:

            print(utils.color_text(f"Current working directory: {Path(__file__).parent}", 'info'))
            sys.exit(0)

        if len(sys.argv) > 1 and sys.argv[1] == ".":
            project_path = os.getcwd()
        elif len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            if sys.argv[1] not in ["unpack", "open", "conf", "reset", "redo", "update", "uninstall",
                                   "version", "info", "pwd"]:
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

    if not config['project_path']:
        print(utils.color_text("Error: Project path is required!", 'error'))
        return

    if not os.path.isdir(config['project_path']):
        print(utils.color_text(f"Error: Directory '{config['project_path']}' does not exist!", 'error'))
        return

    try:
        root_path = os.path.normpath(config['project_path'])
        root_name = os.path.basename(root_path)

        print(utils.color_text("\nScanning project structure...", 'info'))
        tree, files = utils.generate_file_tree(root_path, config)

        print(utils.color_text("\nGenerating documentation...", 'info'))
        md_content = (
            f"# Project Structure: {root_name}\n\n"
            f"```\n{root_name}/\n{tree}\n```\n\n"
            f"# Files Content\n\n{utils.get_file_contents(files)}"
        )

        output_path = Path(config['output_path'])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        utils.save_config(config)
        utils.save_latest_paths(str(output_path))

        print(utils.color_text("\nDocumentation generated successfully!", 'success'))
        print(utils.color_text(f"Output file: {output_path}", 'path'))
        print(utils.color_text(f"Total files processed: {len(files)}", 'info'))

    except Exception as e:
        print(utils.color_text(f"\nError: {str(e)}", 'error'))


if __name__ == "__main__":
    main()