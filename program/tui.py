from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Button, Static, Input, TextArea, DirectoryTree
)
from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual import on, events
from pathlib import Path
import os
import json

from program import utils, config_utils as cfg

import program.commands as commands
from textual.widgets import Markdown as TextualMarkdown


class ConfigEditor(Screen):
    """Экран редактирования конфигурации"""
    CSS = """
    #config-container {
        width: 80%;
        height: 100%;
        margin: 1;
        border: solid $accent;
        padding: 1;
    }
    #config-editor {
        width: 100%;
        height: 80%;
    }
    """

    def compose(self) -> ComposeResult:
        config_path = utils.get_config_path()
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
        except FileNotFoundError:
            config_content = json.dumps(cfg.DEFAULT_CONFIG, indent=2)

        yield Container(
            TextArea(config_content, id="config-editor", language="json"),
            Button("Сохранить", id="save-config", variant="primary"),
            Button("Отмена", id="cancel-config"),
            id="config-container"
        )

    @on(Button.Pressed, "#save-config")
    def save_config(self):
        editor = self.query_one("#config-editor")
        try:
            json.loads(editor.text)
            config_path = utils.get_config_path()
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(editor.text)
            self.notify("Конфигурация сохранена!", severity="success")
            self.app.pop_screen()
        except json.JSONDecodeError as e:
            self.notify(f"Ошибка в JSON: {str(e)}", severity="error")

    @on(Button.Pressed, "#cancel-config")
    def cancel_edit(self):
        self.app.pop_screen()


class PathInputScreen(Screen):
    CSS = """
    #path-container {
        width: 80%;
        height: 24;
        min-height: 24; 
        margin: 1;
        border: solid $accent;
        padding: 2;
    }

    Static {
        width: 100%;
        margin-bottom: 1;
    }
    Input {
        width: 100%;
        margin-bottom: 2;
    }
    Button {
        width: 20%;
        margin: 1 2;
    }
    """

    def __init__(self, title: str, default: str = None):
        super().__init__()
        self.title = title
        self.default = default or os.getcwd()

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title),
            Input(value=self.default, placeholder="Введите путь или оставьте текущий", id="path-input"),
            Button("Подтвердить", id="confirm-path", variant="primary"),
            Button("Отмена", id="cancel-path"),
            id="path-container"
        )

    @on(Button.Pressed, "#confirm-path")
    def confirm_path(self):
        path_input = self.query_one("#path-input")
        input_value = path_input.value.strip()

        if input_value == ".":
            input_value = os.getcwd()
        elif not input_value:
            input_value = self.default

        self.dismiss(input_value)

    @on(Button.Pressed, "#cancel-path")
    def cancel_path(self):
        self.dismiss(None)


class UnpackScreen(Screen):
    """Экран распаковки проекта"""
    CSS = """
    #unpack-container {
        width: 80%;
        height: auto;
        min-height: 16;
        margin: 1;
        border: solid $accent;
        padding: 2;
    }
    #unpack-container > Static {
        width: 100%;
        margin-bottom: 1;
    }
    #unpack-container > Input {
        width: 100%;
        margin-bottom: 2;
    }
    #unpack-container > Button {
        width: 40%;
        margin: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Укажите путь к файлу документации:"),
            Input(placeholder="documentation.md", id="doc-path"),
            Static("Укажите целевую папку:"),
            Input(placeholder="./project", id="target-path"),
            Button("Распаковать", id="unpack-btn", variant="primary"),
            Button("Отмена", id="cancel-unpack"),
            id="unpack-container"
        )

    @on(Button.Pressed, "#unpack-btn")
    def do_unpack(self):
        doc_path = self.query_one("#doc-path").value
        target_path = self.query_one("#target-path").value

        if not doc_path or not target_path:
            self.notify("Укажите оба пути!", severity="error")
            return

        try:
            result, text = commands.unpack(doc_path, target_path)

            # Получаем доступ к главному контенту
            content = self.app.query_one("#content")

            clean_text = commands.ansi_to_textual(text)
            content.update(clean_text)

            self.app.pop_screen()
        except Exception as e:
            error_message = str(e)
            content = self.app.query_one("#content")
            content.update(f"[red]Ошибка:[/] {error_message}")
            self.app.pop_screen()


    @on(Button.Pressed, "#cancel-unpack")
    def cancel_unpack(self):
        self.app.pop_screen()



class MarkdownViewer(Screen):
    """Экран для просмотра Markdown с форматированием"""
    CSS = """
       #md-viewer {
           width: 95%;
           height: 90%;
           border: solid $accent;
           padding: 1;
       }
       #md-content {
           width: 100%;
       }      
       """

    def __init__(self, content: str):
        super().__init__()
        self.content = self.sanitize_markdown(content)

    def sanitize_markdown(self, text: str) -> str:
        """Очистка Markdown от ANSI кодов и проблемных символов"""
        text = text.replace("[/]", "").replace("[red]", "").replace("[green]", "")
        return text

    def compose(self) -> ComposeResult:
        yield ScrollableContainer(
            TextualMarkdown(self.content, id="md-content"),
            id="md-viewer"
        )
        yield Button("Закрыть", id="close-md")

    @on(Button.Pressed, "#close-md")
    def close_viewer(self):
        self.app.pop_screen()


class OFPTUI(App):
    """Главный TUI интерфейс"""
    CSS = """
    Screen {
        layout: vertical;
        align: center middle;
    }
    #buttons {
        layout: horizontal;
        width: 100%;
        height: 10%;
        margin-bottom: 1;
        align: center middle;
    }
    #content {
        width: 95%;
        height: 85%;
        border: solid $accent;
        padding: 1;
    }
    Button {
        min-width: 10;
        margin: 1 2;
    }
    Input {
        width: 100%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Выход"),
    ]



    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Button("Сгенерировать", id="generate", variant="success"),
            Button("Открыть док.", id="open_doc"),
            Button("Открыть док. здесь", id="view_md"),
            Button("Открыть конфиг", id="open-config"),
            Button("Редакт. конфиг", id="edit-config"),
            Button("Распаковать", id="unpack"),
            Button("Инфо", id="info"),
            id="buttons"
        )
        yield ScrollableContainer(Static(id="content"))
        yield Footer()

    def action_quit(self):
        self.exit()

    @on(Button.Pressed, "#generate")
    async def on_generate(self):
        """Генерация документации"""
        content = self.query_one("#content")
        content.update("Подготовка к генерации...")

        project_screen = PathInputScreen(
            "Путь к проекту:",
            utils.load_config().get('project_path')
        )

        def handle_project_path(project_path: str | None) -> None:
            if not project_path:
                content.update("Отменено")
                return

            project_path_obj = Path(project_path)
            default_output = str(project_path_obj / "project_documentation.md")

            output_screen = PathInputScreen("Путь для сохранения:", default_output)

            def handle_output_path(output_path: str | None) -> None:
                if not output_path:
                    content.update("Отменено")
                    return

                content.update("Идёт генерация документации...")
                try:
                    result = commands.generate_documentation(project_path, output_path)
                    clean_result = commands.ansi_to_textual(result)
                    content.update(f"Генерация завершена!\n{clean_result}")

                    config = utils.load_config()
                    config['project_path'] = project_path
                    config['output_path'] = output_path
                    utils.save_config(config)

                except Exception as e:
                    content.update(f"Ошибка генерации: {str(e)}")

            self.push_screen(output_screen, handle_output_path)

        self.push_screen(project_screen, handle_project_path)

    @on(Button.Pressed, "#open_doc")
    async def open_documentation(self) -> None:
        """Открытие документации"""
        content = self.query_one("#content")
        content.update("Открытие документации...")

        try:
            path = commands.open_output_file()

            if not path:
                content.update("[red]Документация не найдена![/]")
                return

            content.update(f"[green]Документация открыта:[/]\n{path}")
        except Exception as e:
            content.update(f"[red]Ошибка:[/] {str(e)}")


    @on(Button.Pressed, "#open-config")
    async def on_open_config(self):
        """Открытие конфига"""
        content = self.query_one("#content")
        content.update("Попытка открыть конфиг...")
        try:
            path = commands.open_config_file()

            if not path:
                content.update("[red]Конфиг не найден![/]")
                return

            content.update(f"[green]Конфиг открыт в {path}[/]")
        except Exception as e:
            content.update(f"[red]Ошибка: {str(e)}[/]")

    @on(Button.Pressed, "#edit-config")
    async def on_edit_config(self):
        """Редактирование конфига"""
        await self.push_screen(ConfigEditor())

    @on(Button.Pressed, "#unpack")
    async def on_unpack(self):
        """Распаковка проекта"""
        await self.push_screen(UnpackScreen())



    @on(Button.Pressed, "#info")
    async def on_info(self):
        content = self.query_one("#content")
        try:
            info = commands.ansi_to_textual(commands.print_project_info())
            content.update(info)
        except Exception as e:
            content.update("Error loading info")


    @on(Button.Pressed, "#view_md")
    async def view_markdown(self):
        """Открыть Markdown в отдельном экране"""
        try:
            path = commands.open_output_file(False)

            if not path:
                content = self.query_one("#content")
                content.update("[red]Документация не найдена![/]")
                return

            if path and os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    await self.push_screen(MarkdownViewer(content))
        except Exception as e:
            error_msg = str(e).replace("[", "").replace("]", "")
            self.notify(f"Ошибка: {error_msg}", severity="error")

def run_tui():
    """Запуск TUI интерфейса"""
    app = OFPTUI()
    app.run()
