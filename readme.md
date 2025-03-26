# Генератор документации проектов - One File Project  

*Мощный инструмент для автоматического создания документации проекта*  

## 🎯 Назначение проекта  

Этот инструмент создан для разработчиков и команд, которым нужно:  
- Быстро документировать структуру существующих проектов  
- Создавать интерактивную справку по кодовой базе  
- Анализировать архитектуру legacy-проектов  
- Генерировать Markdown-документацию для GitHub/GitLab  
- Сохранять "снимок" состояния проекта на определенный момент  


Особенно полезен для:
- Новых членов команды для быстрого ознакомления
- Документирования проектов с устаревшей документацией
- Анализа зависимостей между файлами
- Создания документации для проектов с закрытым исходным кодом

## 👀 Ну а если на чистоту, то я знаю что ты будешь использовать его для вайб-кодинга)

---

## 🚀 Быстрый старт  

### Установка  
```bash  
git clone https://github.com/Antongo22/OneFileProject  
pip install colorama  
cd OneFileProject  
python installer.py  # Установка с созданием команды ofp
```
❗️ Эту папку можно удалять, тк программа уже установилась.


После установки можно использовать команду `ofp` из любой директории!

### Деинсталляция  
```bash  
ofp uninstall  # Удаление через установленную команду
# ИЛИ
python installer.py uninstall  # Альтернативный способ
```  

###  Обновление
```bash  
ofp update  # Удаление через установленную команду
# ИЛИ
python installer.py update  # Альтернативный способ
``` 
---

### Основные команды  
```bash  
# Основной режим (интерактивный)  
ofp  

# Быстрые команды:  
ofp open          # Открыть сгенерированную документацию  
ofp conf          # Открыть файл конфигурации  
ofp reset         # Сбросить настройки и выходной файл  
ofp reset -c      # Сбросить только конфигурацию  
ofp reset -o      # Сбросить только выходной файл  
ofp redo          # Перегенерировать документацию (без вопросов)  
ofp help          # Справка (английский)  
ofp help -ru      # Справка на русском  
ofp <dir_path>    # Сделает документацию проекта по пути. Файл будет лежать радом с папкой
ofp .             # Документирование будет выполнено на основе текущей папки
ofp unpack <doc>.md <dir> # Распаковывает документацию
```  

## 🔄 Новые возможности  

### Быстрые команды после установки:  
- `ofp` - интерактивный режим (аналог `python main.py`)  
- `ofp open` - мгновенно открывает документацию  
- `ofp conf` - редактирует конфиг в редакторе по умолчанию  
- `ofp redo` - моментальная перегенерация без вопросов  

### Пример рабочего процесса:  
```bash
ofp .              # Документировать текущую папку
ofp open           # Просмотреть результат
ofp reset -o       # Очистить старую документацию
ofp redo           # Сгенерировать заново
```

Остальные разделы (конфигурация, поддерживаемые языки и т.д.) остаются без изменений, только заменяются вызовы `python main.py` на `ofp` где необходимо.

## Ссылки
- [Изменения](./changelog.md)
