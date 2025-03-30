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
from typing import Optional

from program import utils, config_utils as cfg
from program.commands import (
    open_output_file,
    open_config_file,
    print_project_info,
    generate_documentation,
    unpack
)
import program.commands as commands

class ConfigEditor(Screen):
    """Экран редактирования конфигурации"""
    CSS = """
    #config-container {
        width: 80%;
        height: 80%;
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
            # Валидация JSON
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
    """Экран ввода пути"""
    CSS = """
    #path-container {
        width: 80%;
        height: 30%;
        margin: 1;
        border: solid $accent;
        padding: 1;
    }
    """

    def __init__(self, title: str, default: str = ""):
        super().__init__()
        self.title = title
        self.default = default

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title),
            Input(placeholder=self.default, id="path-input"),
            Button("Подтвердить", id="confirm-path", variant="primary"),
            Button("Отмена", id="cancel-path"),
            id="path-container"
        )

    @on(Button.Pressed, "#confirm-path")
    def confirm_path(self):
        path_input = self.query_one("#path-input")
        self.dismiss(path_input.value or self.default)

    @on(Button.Pressed, "#cancel-path")
    def cancel_path(self):
        self.dismiss(None)


class UnpackScreen(Screen):
    """Экран распаковки проекта"""
    CSS = """
    #unpack-container {
        width: 80%;
        height: 40%;
        margin: 1;
        border: solid $accent;
        padding: 1;
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
            result = unpack(doc_path, target_path)
            self.notify(result, severity="success")
            self.app.pop_screen()
        except Exception as e:
            self.notify(f"Ошибка: {str(e)}", severity="error")

    @on(Button.Pressed, "#cancel-unpack")
    def cancel_unpack(self):
        self.app.pop_screen()


class OFPTUI(App):
    """Главный TUI интерфейс"""
    CSS = """
    Screen {
        layout: vertical;
    }
    #buttons {
        layout: horizontal;
        width: 100%;
        height: 10%;
        margin-bottom: 1;
    }
    #content {
        width: 100%;
        height: 90%;
        border: solid $accent;
        padding: 1;
    }
    Button {
        margin: 1;
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


    async def get_path_input(self, title: str, default: str = "") -> Optional[str]:
        """Универсальный метод для ввода пути"""
        screen = PathInputScreen(title, default)
        result = await self.push_screen_wait(screen)
        return result if result else None
    #
    # @on(Button.Pressed, "#generate")
    # async def on_generate(self):
    #     """Генерация документации"""
    #     content = self.query_one("#content")
    #     content.update("Подготовка к генерации...")
    #
    #     project_path = await self.get_path_input(
    #         "Путь к проекту:",
    #         utils.load_config().get('project_path', os.getcwd())
    #     )
    #     if not project_path:
    #         return
    #
    #     default_output = utils.load_config().get('output_path',
    #                                              str(Path(project_path) / "project_documentation.md"))
    #     output_path = await self.get_path_input("Путь для сохранения:", default_output)
    #     if not output_path:
    #         return
    #
    #     content.update("Идёт генерация документации...")
    #     result = generate_documentation(project_path, output_path)
    #     content.update(result)

    @on(Button.Pressed, "#open_doc")
    async def open_documentation(self) -> None:
        """Открытие документации"""
        content = self.query_one("#content")
        content.update("Открытие документации...")

        try:
            path = commands.open_output_file()
            content.update(f"[green]Документация открыта:[/]\n{path}")
        except Exception as e:
            content.update(f"[red]Ошибка:[/] {str(e)}")

    @on(Button.Pressed, "#open-config")
    async def on_open_config(self):
        """Открытие конфига"""
        content = self.query_one("#content")
        content.update("Попытка открыть конфиг...")
        try:
            open_config_file()
            content.update("[green]Конфиг открыт в ассоциированном приложении[/]")
        except Exception as e:
            content.update(f"[red]Ошибка: {str(e)}[/]")

    @on(Button.Pressed, "#edit-config")
    async def on_edit_config(self):
        """Редактирование конфига"""
        await self.push_screen(ConfigEditor())

    # @on(Button.Pressed, "#unpack")
    # async def on_unpack(self):
    #     """Распаковка проекта"""
    #     await self.push_screen(UnpackScreen())

    @staticmethod
    def ansi_to_textual(text: str) -> str:
        """Конвертирует ANSI-цвета в Textual-разметку"""
        color_map = {
            '\x1b[35m': '[magenta]',
            '\x1b[36m': '[cyan]',
            '\x1b[0m': '[/]'
        }
        for ansi, textual in color_map.items():
            text = text.replace(ansi, textual)
        return text

    @on(Button.Pressed, "#info")
    async def on_info(self):
        content = self.query_one("#content")
        try:
            info = self.ansi_to_textual(commands.print_project_info())
            content.update(info)
        except Exception as e:
            content.update("Error loading info")





def run_tui():
    """Запуск TUI интерфейса"""
    app = OFPTUI()
    app.run()