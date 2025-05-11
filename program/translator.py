import json
import os
import logging
from pathlib import Path
from typing import Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('translator')


class Translator:
    """Простой класс переводчика, который читает переводы из JSON файлов"""

    def __init__(self, locale_dir: str = "locales"):
        # Определяем абсолютный путь к папке переводов
        script_dir = Path(__file__).parent
        self.locale_dir = script_dir / locale_dir
        
        self.translations = {}
        self.current_lang = "en"
        self.default_lang = "en"

        # Создаем директорию переводов, если она не существует
        os.makedirs(self.locale_dir, exist_ok=True)
        self.load_translations()

    def load_translations(self):
        """Загружает переводы из JSON файлов"""
        for lang_file in self.locale_dir.glob("*.json"):
            lang = lang_file.stem
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    self.translations[lang] = json.load(f)
                    logger.debug(f"Загружен файл локализации: {lang}")
            except Exception as e:
                logger.error(f"Ошибка загрузки файла {lang_file}: {str(e)}")

    def set_language(self, lang: str):
        """Устанавливает текущий язык"""
        if lang in self.translations:
            self.current_lang = lang
            return True
        return False

    def translate(self, key: str, **kwargs):
        """
        Получает перевод по ключу
        :param key: Ключ в формате 'category.subcategory.key'
        :param kwargs: Параметры для форматирования
        """
        if not key:
            return key

        # Разбиваем ключ на части
        parts = key.split('.')

        # Получаем перевод из текущего языка
        result = self._find_translation(self.current_lang, parts)

        # Если перевод не найден, пробуем получить из языка по умолчанию
        if result is None and self.current_lang != self.default_lang:
            result = self._find_translation(self.default_lang, parts)

        # Если перевод все еще не найден, возвращаем последнюю часть ключа
        if result is None:
            result = parts[-1].replace('_', ' ').capitalize()

        # Применяем параметры форматирования
        if kwargs and isinstance(result, str):
            try:
                result = result.format(**kwargs)
            except Exception as e:
                logger.warning(f"Ошибка форматирования для {key}: {str(e)}")

        return result

    def _find_translation(self, lang, parts):
        """Находит перевод по частям ключа"""
        if lang not in self.translations:
            return None

        current = self.translations[lang]
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current if isinstance(current, str) else None


# Создаем глобальный экземпляр переводчика
translator = Translator()