import json
from pathlib import Path
from typing import Dict, Any


class Translator:
    def __init__(self, locale_dir: str = "locales"):
        self.locale_dir = Path(locale_dir)
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.current_lang = "en"
        self.load_translations()


    def load_translations(self):
        """Загружает все доступные переводы"""
        for lang_file in self.locale_dir.glob("*.json"):
            lang = lang_file.stem
            with open(lang_file, "r", encoding="utf-8") as f:
                self.translations[lang] = json.load(f)

    def set_language(self, lang: str):
        """Устанавливает текущий язык"""
        if lang in self.translations:
            self.current_lang = lang
            return True
        return False

    def translate(
            self,
            key: str,
            default: str = None,
            **kwargs
    ) -> str:
        """
        Получает перевод по ключу
        :param key: Ключ в формате 'category.subcategory.key'
        :param default: Текст по умолчанию, если перевод не найден
        :param kwargs: Параметры для подстановки в строку
        """
        keys = key.split('.')
        current = self.translations.get(self.current_lang, {})

        try:
            for k in keys:
                current = current[k]

            if isinstance(current, str) and kwargs:
                return current.format(**kwargs)
            return current
        except (KeyError, AttributeError):
            return default or key


translator = Translator()