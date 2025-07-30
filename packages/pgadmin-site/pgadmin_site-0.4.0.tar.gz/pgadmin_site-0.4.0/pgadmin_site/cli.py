"""
CLI интерфейс для запуска pgadmin-site из командной строки.
"""

import click
from .main import site

@click.command()
@click.option('--host', '-h', default='localhost', help='Адрес сервера PostgreSQL')
@click.option('--port', '-p', default=5432, help='Порт PostgreSQL')
@click.option('--username', '-u', default='postgres', help='Имя пользователя')
@click.option('--password', '-P', prompt=True, hide_input=True, help='Пароль')
@click.option('--database', '-d', default='postgres', help='Имя базы данных')
@click.option('--web-port', '-w', default=5000, help='Порт для веб-интерфейса')
@click.option('--debug', is_flag=True, help='Включить режим отладки')
@click.option('--icon', help='Путь к файлу иконки')
@click.option('--foto', help='Путь к файлу изображения с опциональным флагом перемещаемости (true/false)')
@click.option('--card', help='Название шаблона карточки (без .json)')
def main(host, port, username, password, database, web_port, debug, icon, foto, card):
    """Запуск локального веб-интерфейса для работы с PostgreSQL."""
    site(
        host=host,
        port=port,
        username=username,
        password=password,
        database=database,
        web_port=web_port,
        debug=debug,
        icon=icon,
        foto=foto,
        card=card
    )

if __name__ == '__main__':
    main() 