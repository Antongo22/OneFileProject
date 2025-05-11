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
from program.translator import translator

# Общий CSS для всего приложения, чтобы избежать выделения текста на кнопках
SHARED_CSS = """
/* Глобальный стиль для отключения выделения текста в кнопках */
Button:focus > .button--content {
    color: $text;
    text-style: none;
}

Button.-active > .button--content {
    color: $text;
    text-style: none;
}

/* Стиль для активной кнопки (выбранный элемент) */
Button.selected-lang {
    background: $accent;
}
"""


class ConfigEditor(Screen):
    """Экран редактирования конфигурации"""
    CSS = SHARED_CSS + """
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
    Button {
        width: 20%;
        margin: 1 2;
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
            Button(translator.translate('common.save'), id="save-config", variant="primary"),
            Button(translator.translate('common.cancel'), id="cancel-config"),
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
            self.notify(translator.translate('tui.config_saved'), severity="success")
            self.app.pop_screen()
        except json.JSONDecodeError as e:
            self.notify(translator.translate('tui.json_error', error=str(e)), severity="error")

    @on(Button.Pressed, "#cancel-config")
    def cancel_edit(self):
        self.app.pop_screen()


class PathInputScreen(Screen):
    CSS = SHARED_CSS + """
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
            Input(value=self.default, placeholder=translator.translate('tui.enter_path'), id="path-input"),
            Button(translator.translate('tui.confirm_path'), id="confirm-path", variant="primary"),
            Button(translator.translate('common.cancel'), id="cancel-path"),
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
    CSS = SHARED_CSS + """
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
        width: 20%;
        margin: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Container(
            Static(translator.translate('tui.doc_file_label')),
            Input(placeholder="/path/to/documentation.md", id="doc-path"),
            Static(translator.translate('tui.target_dir_label')),
            Input(placeholder="/path/to/target/directory", id="target-path"),
            Button(translator.translate('tui.unpack_button_confirm'), id="do-unpack", variant="primary"),
            Button(translator.translate('common.cancel'), id="cancel-unpack"),
            id="unpack-container"
        )

    @on(Button.Pressed, "#do-unpack")
    def do_unpack(self):
        doc_input = self.query_one("#doc-path")
        target_input = self.query_one("#target-path")

        doc_path = doc_input.value.strip()
        target_path = target_input.value.strip()

        if not doc_path or not target_path:
            self.notify(translator.translate('tui.unpack_paths_required'), severity="error")
            return

        try:
            result = commands.unpack(doc_path, target_path)
            if result[0]:
                self.notify(result[1], severity="success")
                self.app.pop_screen()
            else:
                self.notify(translator.translate('tui.unpack_error_red', error=result[1]), severity="error")
        except Exception as e:
            self.notify(translator.translate('tui.unpack_error_red', error=str(e)), severity="error")

    @on(Button.Pressed, "#cancel-unpack")
    def cancel_unpack(self):
        self.app.pop_screen()


class LanguageScreen(Screen):
    """Экран выбора языка"""
    CSS = SHARED_CSS + """
    #lang-container {
        width: 30%;
        height: 15;
        margin: 1;
        border: solid $accent;
        padding: 2;
    }
    #lang-container > Static {
        width: 100%;
        margin-bottom: 1;
        text-align: center;
    }
    #cancel-button-container {
        width: 100%;
        align: center middle;
    }
    #cancel-lang {
        width: 25%;
        margin: 1 0;
        /* Отключение выделения текста не поддерживается в Textual */
    }
    
    Button {
        /* Отключение выделения текста не поддерживается в Textual */
    }
    #lang-buttons {
        layout: horizontal;
        width: 100%;
        align: center middle;
    }
    .selected-lang {
        background: $accent;
    }
    """
    
    def compose(self) -> ComposeResult:
        # Получаем текущий язык
        current_lang = translator.current_lang
        
        yield Container(
            Static(translator.translate('tui.choose_language')),
            Container(
                Button(
                    "English", 
                    id="lang-en",
                    classes="selected-lang" if current_lang == "en" else ""
                ),
                Button(
                    "Русский", 
                    id="lang-ru",
                    classes="selected-lang" if current_lang == "ru" else ""
                ),
                id="lang-buttons"
            ),
            Container(
                Button(translator.translate('common.cancel'), id="cancel-lang"),
                id="cancel-button-container"
            ),
            id="lang-container"
        )
    
    @on(Button.Pressed, "#lang-en")
    def set_english(self):
        global restart_required
        
        success, message = commands.change_language("en")
        if success:
            # Устанавливаем флаг необходимости перезапуска
            restart_required = True
            
            # Закрываем этот экран
            self.app.pop_screen()
            
            # Сразу закрываем приложение для перезапуска
            self.app.exit()
        else:
            self.notify(message, severity="error")
            self.app.pop_screen()

    @on(Button.Pressed, "#lang-ru")
    def set_russian(self):
        global restart_required
        
        success, message = commands.change_language("ru")
        if success:
            # Устанавливаем флаг необходимости перезапуска
            restart_required = True
            
            # Закрываем этот экран
            self.app.pop_screen()
            
            # Сразу закрываем приложение для перезапуска
            self.app.exit()
        else:
            self.notify(message, severity="error")
            self.app.pop_screen()
        
    @on(Button.Pressed, "#cancel-lang")
    def cancel_lang(self):
        self.app.pop_screen()


class MarkdownViewer(Screen):
    """Экран для просмотра Markdown с форматированием"""
    CSS = SHARED_CSS + """
    Screen {
        align: center middle;
    }

    #md-content {
        width: 95%;
        height: 85%;
        layout: vertical;
        align: center top;
    }

    #md-viewer {
        width: 100%;
        height: 85%;
        border: solid $accent;
        padding: 1;
    }

    #close-button-container {
        width: 100%;
        height: auto;
        margin-top: 1;
        align: center middle;
    }

    #close-viewer {
        width: 15%;
        margin: 1;
        /* Отключение выделения текста не поддерживается в Textual */
    }
    
    Button {
        /* Отключение выделения текста не поддерживается в Textual */
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
        # Создаем контейнер для всего содержимого
        with Container(id="md-content"):
            # Markdown в скроллируемом контейнере
            yield ScrollableContainer(
                TextualMarkdown(self.content),
                id="md-viewer"
            )
            # Отдельный контейнер для кнопки
            with Container(id="close-button-container"):
                yield Button(translator.translate('common.close'), id="close-viewer")

    @on(Button.Pressed, "#close-viewer")
    def close_viewer(self):
        self.app.pop_screen()


class OFPTUI(App):
    """Главный TUI интерфейс"""
    CSS = SHARED_CSS + """
    Screen {
        layout: vertical;
        align: center middle;
    }
    #buttons {
        layout: vertical;
        width: 100%;
        height: auto;
        align: center middle;
    }
    #button-row1, #button-row2 {
        layout: horizontal;
        width: 100%;
        height: auto;
        align: center middle;
        margin: 1 0;
    }
    Button {
        width: 15%;
        margin: 0 1;
    }
    
    /* Убираем выделение текста при нажатии */
    Button:focus > .button--content {
        color: $text;
        text-style: none;
    }
    
    Button.-active > .button--content {
        color: $text;
        text-style: none;
    }
    #content {
        width: 95%;
        height: 30;
        border: solid $accent;
        margin: 1;
        padding: 1;
        background: $boost;
        overflow: auto;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Exit"),
    ]

    def compose(self) -> ComposeResult:
        # Создаем Header и Footer без параметров, а затем настраиваем их
        yield Header(id="header", name="header")
        yield Footer(id="footer", name="footer")

        with Container(id="buttons"):
            # Первый ряд кнопок
            with Container(id="button-row1"):
                yield Button(translator.translate('tui.generate_button'), id="generate", variant="primary")
                yield Button(translator.translate('tui.open_docs_button'), id="open_doc")
                yield Button(translator.translate('tui.config_button'), id="open-config")
                yield Button(translator.translate('tui.edit_config_button'), id="edit-config")
            
            # Второй ряд кнопок
            with Container(id="button-row2"):
                yield Button(translator.translate('tui.unpack_button'), id="unpack")
                yield Button(translator.translate('tui.info_button'), id="info")
                yield Button(translator.translate('tui.view_md_button'), id="view_md")
                yield Button(translator.translate('tui.language_button'), id="change-lang")

        yield Static(translator.translate('tui.app_title'), id="content")
        
    def on_mount(self) -> None:
        """Настраиваем заголовок и нижний колонтитул после монтирования"""
        # Получаем компоненты по их ID
        header = self.query_one("#header", Header)
        footer = self.query_one("#footer", Footer)
        
        # Устанавливаем текст
        header.tall = True
        header.title = translator.translate('ui.header_title')
        
        # Настраиваем текст подсказки в нижнем колонтитуле
        footer.highlight_key = "?"
        footer.highlight_name = translator.translate('ui.footer_help')

    def action_quit(self):
        self.exit()

    @on(Button.Pressed, "#generate")
    async def on_generate(self) -> None:
        """Генерация документации"""
        content = self.query_one("#content")
        content.update(translator.translate('tui.generation_preparing'))

        project_screen = PathInputScreen(
            translator.translate('tui.project_path_title'),
            utils.load_config().get('project_path')
        )

        def handle_project_path(project_path: str | None) -> None:
            if not project_path:
                content.update(translator.translate('tui.generation_canceled'))
                return

            content.update(translator.translate('tui.generation_started'))

            project_path_obj = Path(project_path)
            default_output = str(project_path_obj / "project_documentation.md")

            output_screen = PathInputScreen(translator.translate('tui.output_path_title'), default_output)

            def handle_output_path(output_path: str | None) -> None:
                if not output_path:
                    content.update(translator.translate('tui.generation_canceled'))
                    return

                content.update(translator.translate('tui.generation_started'))
                try:
                    result = commands.generate_documentation(project_path, output_path)
                    clean_result = commands.ansi_to_textual(result)
                    content.update(translator.translate('tui.generation_complete', result=clean_result))

                    config = utils.load_config()
                    config['project_path'] = project_path
                    config['output_path'] = output_path
                    utils.save_config(config)

                except Exception as e:
                    content.update(translator.translate('tui.generation_error', error=str(e)))

            self.push_screen(output_screen, handle_output_path)

        self.push_screen(project_screen, handle_project_path)

    @on(Button.Pressed, "#open_doc")
    async def open_documentation(self) -> None:
        """Открытие документации"""
        content = self.query_one("#content")
        content.update(translator.translate('tui.opening_doc'))

        try:
            path = commands.open_output_file()

            if not path:
                content.update(f"[red]{translator.translate('tui.doc_not_found_red')}[/]")
                return

            content.update(f"[green]{translator.translate('tui.doc_opened_green', path=path)}[/]")
        except Exception as e:
            content.update(f"[red]{translator.translate('tui.open_error_red', error=str(e))}[/]")


    @on(Button.Pressed, "#open-config")
    async def on_open_config(self):
        """Открытие конфига"""
        content = self.query_one("#content")
        content.update(translator.translate('tui.opening_config'))
        try:
            path = commands.open_config_file()

            if not path:
                content.update(f"[red]{translator.translate('tui.config_not_found_red')}[/]")
                return

            content.update(f"[green]{translator.translate('tui.config_opened_green', path=path)}[/]")
        except Exception as e:
            content.update(f"[red]{translator.translate('tui.config_error_red', error=str(e))}[/]")

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
            content.update(translator.translate('tui.info_error'))


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
            self.notify(translator.translate('tui.open_error_red', error=error_msg), severity="error")
            
    def update_interface_language(self):
        """Обновляет язык интерфейса без перезапуска приложения"""
        # Запоминаем текущее состояние для восстановления
        try:
            current_content = self.query_one("#content").render()
        except Exception:
            current_content = translator.translate('tui.app_title')
        
        # Обновляем заголовок
        header = self.query_one("#header", Header)
        header.title = translator.translate('common.header_title')
        
        # Обновляем футер
        footer = self.query_one("#footer", Footer)
        footer.highlight_key = translator.translate('tui.footer_highlight_key')
        
        # Обновляем тексты на всех кнопках
        # Первый ряд
        self.query_one("#generate").label = translator.translate('tui.generate_button')
        self.query_one("#open_doc").label = translator.translate('tui.open_docs_button')
        self.query_one("#open-config").label = translator.translate('tui.config_button')
        self.query_one("#edit-config").label = translator.translate('tui.edit_config_button')
        # Второй ряд
        self.query_one("#unpack").label = translator.translate('tui.unpack_button')
        self.query_one("#info").label = translator.translate('tui.info_button')
        self.query_one("#view_md").label = translator.translate('tui.view_md_button')
        self.query_one("#change-lang").label = translator.translate('tui.language_button')
        
        # Восстанавливаем содержимое
        content = self.query_one("#content")
        content.update(current_content)
        
    @on(Button.Pressed, "#change-lang")
    async def on_change_language(self):
        """Смена языка интерфейса"""
        await self.push_screen(LanguageScreen())

# Глобальная переменная для отслеживания необходимости перезапуска
restart_required = False

def run_tui():
    """Запуск TUI интерфейса"""
    global restart_required
    
    # Запускаем приложение
    app = OFPTUI()
    app.run()
    
    # Если требуется перезапуск, запускаем TUI снова
    if restart_required:
        restart_required = False
        run_tui()
