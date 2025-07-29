"""
CLI интерфейс для запуска pgadmin-site из командной строки.
"""

import click
from .main import site

@click.command()
@click.option('--host', '-h', default='localhost', help='Хост PostgreSQL сервера')
@click.option('--port', '-p', default=5432, help='Порт PostgreSQL сервера')
@click.option('--username', '-u', default='postgres', help='Имя пользователя PostgreSQL')
@click.option('--password', '-P', prompt=True, hide_input=True, help='Пароль PostgreSQL')
@click.option('--database', '-d', default='postgres', help='Имя базы данных PostgreSQL')
@click.option('--web-port', '-w', default=5000, help='Порт для веб-интерфейса')
@click.option('--debug', is_flag=True, help='Включить режим отладки')
def main(host, port, username, password, database, web_port, debug):
    """
    Запустить локальный веб-интерфейс для работы с таблицами PostgreSQL.
    """
    site(
        host=host,
        port=port,
        username=username,
        password=password,
        database=database,
        web_port=web_port,
        debug=debug
    )

if __name__ == '__main__':
    main() 