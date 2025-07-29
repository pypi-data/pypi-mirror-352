# PGAdmin Site

Библиотека для создания локального веб-интерфейса для работы с таблицами PostgreSQL.

## Установка

```bash
pip install pgadmin-site
```

## Использование

```python
from pgadmin_site import site

# Запустить локальный сайт для работы с базой данных
site(
    host="localhost",
    port=5432,
    username="postgres",
    password="password",
    database="your_database",
    web_port=5000  # Порт для веб-интерфейса
)
```

## Возможности

- Просмотр всех таблиц в базе данных
- Навигация между таблицами через кнопки или выпадающий список
- Редактирование строк, столбцов и отдельных ячеек
- Удаление существующих данных
- Добавление новых записей

## Требования

- Python 3.8+
- PostgreSQL

## Лицензия

MIT 

## Команды CLI

- `pgadmin-site` — запуск локального веб-интерфейса для работы с PostgreSQL. Поддерживает параметры:
  - `--host`, `-h` — адрес сервера PostgreSQL (по умолчанию localhost)
  - `--port`, `-p` — порт PostgreSQL (по умолчанию 5432)
  - `--username`, `-u` — имя пользователя (по умолчанию postgres)
  - `--password`, `-P` — пароль (запрашивается интерактивно)
  - `--database`, `-d` — имя базы данных (по умолчанию postgres)
  - `--web-port`, `-w` — порт для веб-интерфейса (по умолчанию 5000)
  - `--debug` — режим отладки

- `from pgadmin_site import tkinter_card_designer` — запуск визуального редактора карточек на Tkinter:
  - Позволяет создавать SVG-шаблоны карточек с drag&drop, формулами, кнопками, фильтрами и связями с БД.

- `from pgadmin_site import create_module_file` — генерация примеров Tkinter-карточек:
  - `create_module_file('modul(2)')`, `create_module_file('modul(3)')`, `create_module_file('modul(4)')` — создаёт примеры модулей для работы с карточками и БД.

## Основные возможности

- Просмотр и редактирование таблиц PostgreSQL через веб-интерфейс (Flask + Bootstrap)
- Визуальный редактор карточек (Tkinter): поддержка фигур, формул, drag&drop столбцов, кнопок с фильтрами
- Автоматическое построение JOIN по связям, подстановка данных из связанных таблиц
- Кнопки на карточках с визуальным редактором запроса и фильтрами (AND/OR, подстановка из карточки)
- Импорт/экспорт шаблонов карточек в JSON
- Удаление карточки и связанных данных через модальное окно
- Совместимость с любыми структурами БД PostgreSQL

## Пример запуска

```bash
pgadmin-site --host localhost --port 5432 --username postgres --database mydb --web-port 5000
```

## Пример запуска редактора карточек

```python
from pgadmin_site import tkinter_card_designer
tkinter_card_designer(username="postgres", password="пароль", database="mydb")
``` 