"""
Основной модуль, содержащий функцию site для создания веб-интерфейса.
"""

import os
import logging
from typing import Optional
import psycopg2
import shutil
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, flash, send_from_directory
from sqlalchemy import create_engine, MetaData, Table, Column, inspect, text, select
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy import SQLAlchemy
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def site(host: str, 
         port: int = 5432, 
         username: str = "postgres", 
         password: str = "", 
         database: str = "postgres", 
         web_port: int = 5000,
         debug: bool = False,
         card: str = None,
         icon: str = None,
         foto: str = None):
    """
    Создать и запустить локальный веб-сайт для работы с таблицами PostgreSQL или карточками.
    Args:
        host: Хост PostgreSQL сервера
        port: Порт PostgreSQL сервера
        username: Имя пользователя PostgreSQL
        password: Пароль PostgreSQL
        database: Имя базы данных PostgreSQL
        web_port: Порт для веб-интерфейса
        debug: Включить режим отладки
        card: Название шаблона карточки (без .json) для отображения карточек вместо таблиц
        icon: Путь к файлу иконки (.jpg, .png или .jpeg)
        foto: Путь к файлу изображения (.jpg, .png или .jpeg) с опциональным параметром movable (true/false)
    """
    # Создаем Flask приложение
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    app.config['DEBUG'] = debug
    
    # Проверка и установка иконки
    if icon:
        if not os.path.exists(icon):
            raise ValueError(f"Файл иконки не найден: {icon}")
        if not icon.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise ValueError("Иконка должна быть в формате .jpg, .jpeg или .png")
        
        # Копируем иконку в статическую директорию
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        icon_filename = 'favicon' + os.path.splitext(icon)[1]
        icon_path = os.path.join(static_dir, icon_filename)
        shutil.copy2(icon, icon_path)
        
        # Добавляем маршрут для фавикона
        @app.route('/favicon.ico')
        def favicon():
            return send_from_directory(static_dir, icon_filename)

    # Обработка параметра foto
    foto_movable = False
    if foto:
        foto_parts = foto.split()
        foto_path = foto_parts[0]
        foto_movable = len(foto_parts) > 1 and foto_parts[1].lower() == 'true'
        
        if not os.path.exists(foto_path):
            raise ValueError(f"Файл изображения не найден: {foto_path}")
        if not foto_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise ValueError("Изображение должно быть в формате .jpg, .jpeg или .png")
        
        # Копируем изображение в статическую директорию
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        foto_filename = 'foto' + os.path.splitext(foto_path)[1]
        foto_path_dest = os.path.join(static_dir, foto_filename)
        shutil.copy2(foto_path, foto_path_dest)
        
        # Создаем файл для хранения позиции изображения
        position_file = os.path.join(static_dir, 'foto_position.json')
        if not os.path.exists(position_file):
            with open(position_file, 'w') as f:
                json.dump({'x': 0, 'y': 0}, f)
        
        # Добавляем маршруты для работы с изображением
        @app.route('/foto')
        def get_foto():
            return send_from_directory(static_dir, foto_filename)
        
        @app.route('/foto/position', methods=['GET', 'POST'])
        def foto_position():
            if request.method == 'POST':
                position = request.json
                with open(position_file, 'w') as f:
                    json.dump(position, f)
                return jsonify({'status': 'success'})
            else:
                with open(position_file, 'r') as f:
                    return jsonify(json.load(f))
    
    # Настраиваем подключение к базе данных
    connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    # Создаем прямое подключение к базе данных через SQLAlchemy
    # вместо использования db.engine, которое требует контекст приложения
    engine = create_engine(connection_string)
    
    # Получаем метаданные базы данных
    metadata = MetaData()
    inspector = inspect(engine)

    def load_card_template(card_name):
        # Если card_name — это путь к существующему файлу, используем его напрямую
        if os.path.isfile(card_name):
            path = card_name
        else:
            # Если card_name оканчивается на .json, не добавляем ещё раз
            if card_name.endswith('.json'):
                fname = card_name
            else:
                fname = f"{card_name}.json"
            # Сначала ищем в текущей директории запуска
            cwd_path = os.path.abspath(fname)
            if os.path.isfile(cwd_path):
                path = cwd_path
            else:
                # По умолчанию ищем в стандартной папке
                path = os.path.join(os.path.dirname(__file__), "templates", "cards", fname)
                if not os.path.isfile(path):
                    return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def eval_formula(formula, row):
        import decimal, datetime, re
        # ВРЕМЕННО: логируем все ключи строки
        logging.info(f'ROW KEYS: {list(row.keys())}, ROW: {row}')
        if not formula:
            return ''
        f = formula
        # Собираем маппинг коротких имён
        short_map = {}
        for k, v in row.items():
            if '.' in k:
                short = k.split('.', 1)[1]
                if short not in short_map:
                    short_map[short] = k
                else:
                    short_map[short] = None  # Неуникальное короткое имя
            else:
                short_map[k] = k
        # Подстановка значений
        def repl(m):
            key = m.group(1)
            full_key = key
            if key not in row:
                # Пробуем найти по короткому имени
                full_key = short_map.get(key)
            val = row.get(full_key)
            if isinstance(val, decimal.Decimal):
                val = float(val)
            elif isinstance(val, datetime.date):
                val = val.isoformat()
            return repr(val) if val is not None else 'None'
        f = re.sub(r'\{([\w\.]+)\}', repl, f)
        try:
            return str(eval(f))
        except Exception as e:
            return f"[Ошибка формулы: {e}]"

    @app.route('/')
    def index():
        if card:
            card_template = load_card_template(card)
            if not card_template:
                return render_template('error.html', error=f"Шаблон карточки '{card}' не найден.")
            table_names = inspector.get_table_names()
            data = []
            if table_names:
                # --- Собираем все нужные (таблица, столбец) из шаблона ---
                needed = set()
                used_tables = []
                import re
                for fig in card_template:
                    db_col = fig.get('db_column')
                    db_table = fig.get('db_table')
                    if db_col and db_table and db_col not in (None, '', 'None') and db_table not in (None, '', 'None'):
                        needed.add((db_table, db_col))
                        if db_table not in used_tables:
                            used_tables.append(db_table)
                    # --- Автоматически добавляем поля из формул ---
                    if fig.get('formula'):
                        for m in re.findall(r'\{([\w\.]+)\}', fig['formula']):
                            if '.' in m:
                                t, c = m.split('.', 1)
                                needed.add((t, c))
                                if t not in used_tables:
                                    used_tables.append(t)
                            else:
                                # Короткое имя: добавим во все таблицы, если уникально
                                for t in table_names:
                                    columns = inspector.get_columns(t)
                                    if m in [col['name'] for col in columns]:
                                        needed.add((t, m))
                                        if t not in used_tables:
                                            used_tables.append(t)
                # --- Автоматически строим JOIN по foreign key ---
                if used_tables:
                    main_table = used_tables[0]
                    join_tables = used_tables[1:]
                    # Получаем связи (foreign keys)
                    joins = []
                    fk_map = {}
                    for t in used_tables:
                        fks = inspector.get_foreign_keys(t)
                        for fk in fks:
                            fk_map[(t, tuple(fk['constrained_columns']))] = (fk['referred_table'], tuple(fk['referred_columns']))
                    # Строим цепочку JOIN
                    join_sql = ''
                    prev_table = main_table
                    alias_map = {main_table: 't0'}
                    for i, t in enumerate(join_tables):
                        alias = f't{i+1}'
                        alias_map[t] = alias
                        # Ищем связь с предыдущей таблицей
                        found = False
                        fks = inspector.get_foreign_keys(t)
                        for fk in fks:
                            if fk['referred_table'] == prev_table:
                                join_sql += f' LEFT JOIN "{t}" {alias} ON {alias}."{fk["constrained_columns"][0]}" = {alias_map[prev_table]}."{fk["referred_columns"][0]}"'
                                found = True
                                break
                        if not found:
                            # Пробуем обратную связь
                            fks_prev = inspector.get_foreign_keys(prev_table)
                            for fk in fks_prev:
                                if fk['referred_table'] == t:
                                    join_sql += f' LEFT JOIN "{t}" {alias} ON {alias_map[prev_table]}."{fk["constrained_columns"][0]}" = {alias}."{fk["referred_columns"][0]}"'
                                    found = True
                                    break
                        prev_table = t
                    # Собираем SELECT
                    select_cols = []
                    for t, col in needed:
                        alias = alias_map.get(t, t)
                        select_cols.append(f'{alias}."{col}" AS "{t}.{col}"')
                    select_cols_str = ', '.join(select_cols) if select_cols else '*'
                    sql = f'SELECT {select_cols_str} FROM "{main_table}" t0{join_sql} LIMIT 100'
                    with engine.connect() as connection:
                        result = connection.execute(text(sql))
                        data = [dict(row) for row in result.mappings()]
                else:
                    with engine.connect() as connection:
                        query = text(f'SELECT * FROM "{table_names[0]}" LIMIT 100')
                        result = connection.execute(query)
                        data = list(result.mappings())
            logger.info(f"DATA: {data}")
            return render_template('card_svg.html', card_template=card_template, data=data, card_name=card, abs=abs, eval_formula=eval_formula)
        else:
            try:
                table_names = inspector.get_table_names()
                return render_template('index.html', tables=table_names, current_db=database)
            except SQLAlchemyError as e:
                logger.error(f"Ошибка при подключении к базе данных: {str(e)}")
                return render_template('error.html', error=str(e))
    
    @app.route('/table/<table_name>')
    def view_table(table_name):
        card_name = request.args.get('card') or card
        try:
            # Проверяем, что таблица существует
            if table_name not in inspector.get_table_names():
                abort(404, f"Таблица {table_name} не найдена")
            # Получаем информацию о колонках
            columns = inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]
            # Получаем данные из таблицы
            with engine.connect() as connection:
                query = text(f'SELECT * FROM "{table_name}" LIMIT 100')
                result = connection.execute(query)
                try:
                    rows = list(result.mappings())
                except AttributeError:
                    try:
                        rows = [dict(row) for row in result]
                    except TypeError:
                        rows = list(result)
            all_tables = inspector.get_table_names()
            current_index = all_tables.index(table_name)
            prev_table = all_tables[current_index - 1] if current_index > 0 else None
            next_table = all_tables[current_index + 1] if current_index < len(all_tables) - 1 else None
            return render_template(
                'table.html', 
                table_name=table_name,
                columns=column_names,
                rows=rows,
                all_tables=all_tables,
                prev_table=prev_table,
                next_table=next_table,
                card_name=card_name
            )
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при работе с таблицей {table_name}: {str(e)}")
            return render_template('error.html', error=str(e))
    
    @app.route('/table/<table_name>/edit/<int:row_id>', methods=['GET', 'POST'])
    def edit_row(table_name, row_id):
        card_name = request.args.get('card') or card
        try:
            if table_name not in inspector.get_table_names():
                abort(404, f"Таблица {table_name} не найдена")
            columns = inspector.get_columns(table_name)
            pk_columns = inspector.get_pk_constraint(table_name)['constrained_columns']
            if not pk_columns:
                abort(400, f"Таблица {table_name} не имеет первичного ключа")
            primary_key = pk_columns[0]
            if request.method == 'POST':
                data = {col['name']: request.form.get(col['name']) for col in columns}
                update_parts = [f'"{col}" = :{col}' for col in data.keys()]
                update_sql = f'UPDATE "{table_name}" SET {", ".join(update_parts)} WHERE "{primary_key}" = :row_id'
                with engine.begin() as connection:
                    connection.execute(text(update_sql), {**data, 'row_id': row_id})
                flash('Запись успешно обновлена', 'success')
                return redirect(url_for('view_table', table_name=table_name, card=card_name))
            with engine.connect() as connection:
                query = text(f'SELECT * FROM "{table_name}" WHERE "{primary_key}" = :row_id')
                result = connection.execute(query, {'row_id': row_id})
                row_result = result.fetchone()
                try:
                    row = row_result._asdict()
                except AttributeError:
                    try:
                        row = dict(row_result)
                    except TypeError:
                        row = row_result
            return render_template('edit_row.html', table_name=table_name, row=row, columns=columns, card_name=card_name)
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при редактировании строки: {str(e)}")
            return render_template('error.html', error=str(e))
    
    @app.route('/table/<table_name>/add', methods=['GET', 'POST'])
    def add_row(table_name):
        card_name = request.args.get('card') or card
        try:
            # Проверяем, что таблица существует
            if table_name not in inspector.get_table_names():
                abort(404, f"Таблица {table_name} не найдена")
            columns = inspector.get_columns(table_name)
            if request.method == 'POST':
                data = {}
                for col in columns:
                    value = request.form.get(col['name'])
                    if value or not col.get('nullable', True):
                        data[col['name']] = value
                columns_str = ', '.join([f'"{col}"' for col in data.keys()])
                values_str = ', '.join([f':{col}' for col in data.keys()])
                insert_sql = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({values_str})'
                with engine.begin() as connection:
                    connection.execute(text(insert_sql), data)
                flash('Запись успешно добавлена', 'success')
                return redirect(url_for('view_table', table_name=table_name, card=card_name))
            return render_template('add_row.html', table_name=table_name, columns=columns, card_name=card_name)
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении строки: {str(e)}")
            return render_template('error.html', error=str(e))
    
    @app.route('/table/<table_name>/delete/<int:row_id>', methods=['POST'])
    def delete_row(table_name, row_id):
        """Удалить строку из таблицы"""
        try:
            # Проверяем, что таблица существует
            if table_name not in inspector.get_table_names():
                abort(404, f"Таблица {table_name} не найдена")
            
            # Получаем информацию о первичном ключе
            pk_columns = inspector.get_pk_constraint(table_name)['constrained_columns']
            
            if not pk_columns:
                abort(400, f"Таблица {table_name} не имеет первичного ключа")
            
            primary_key = pk_columns[0]
            
            # Выполняем запрос на удаление
            with engine.begin() as connection:
                delete_sql = f'DELETE FROM "{table_name}" WHERE "{primary_key}" = :row_id'
                connection.execute(text(delete_sql), {'row_id': row_id})
            
            flash('Запись успешно удалена', 'success')
            return redirect(url_for('view_table', table_name=table_name))
        
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении строки: {str(e)}")
            return render_template('error.html', error=str(e))
    
    @app.route('/table/<table_name>/structure')
    def table_structure(table_name):
        card_name = request.args.get('card') or card
        try:
            if table_name not in inspector.get_table_names():
                abort(404, f"Таблица {table_name} не найдена")
            columns = inspector.get_columns(table_name)
            pk_constraint = inspector.get_pk_constraint(table_name)
            pk_columns = pk_constraint['constrained_columns'] if pk_constraint else []
            foreign_keys = inspector.get_foreign_keys(table_name)
            indexes = inspector.get_indexes(table_name)
            return render_template(
                'structure.html',
                table_name=table_name,
                columns=columns,
                pk_columns=pk_columns,
                foreign_keys=foreign_keys,
                indexes=indexes,
                card_name=card_name
            )
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении структуры таблицы: {str(e)}")
            return render_template('error.html', error=str(e))
    
    @app.route('/table/<table_name>/add_column', methods=['GET', 'POST'])
    def add_column(table_name):
        """Добавить новый столбец в таблицу"""
        try:
            # Проверяем, что таблица существует
            if table_name not in inspector.get_table_names():
                abort(404, f"Таблица {table_name} не найдена")
            
            if request.method == 'POST':
                column_name = request.form.get('column_name')
                column_type = request.form.get('column_type')
                nullable = request.form.get('nullable') == 'on'
                default = request.form.get('default')
                
                # Формируем SQL запрос для добавления столбца
                nullable_str = "NULL" if nullable else "NOT NULL"
                default_str = f"DEFAULT {default}" if default else ""
                
                alter_sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_type} {nullable_str} {default_str}'
                
                # Выполняем запрос
                with engine.begin() as connection:
                    connection.execute(text(alter_sql))
                
                flash('Столбец успешно добавлен', 'success')
                return redirect(url_for('table_structure', table_name=table_name))
            
            return render_template('add_column.html', table_name=table_name)
        
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении столбца: {str(e)}")
            return render_template('error.html', error=str(e))
    
    @app.route('/delete_card', methods=['POST'])
    def delete_card():
        card_name = request.args.get('card') or request.form.get('card') or card
        card_key = request.form.get('card_key')
        # Определяем основную таблицу и основной столбец
        card_template = load_card_template(card_name)
        used_tables = []
        for fig in card_template:
            db_col = fig.get('db_column')
            db_table = fig.get('db_table')
            if db_col and db_table and db_col not in (None, '', 'None') and db_table not in (None, '', 'None'):
                if db_table not in used_tables:
                    used_tables.append(db_table)
        if not used_tables:
            return render_template('error.html', error='Не удалось определить основную таблицу для удаления.')
        main_table = used_tables[0]
        # Определяем основной столбец (первый столбец основной таблицы)
        columns = inspector.get_columns(main_table)
        key_col = columns[0]['name']
        # Удаляем сначала из зависимых таблиц (по foreign key), потом из основной
        with engine.begin() as connection:
            # Удаляем из зависимых таблиц
            for t in inspector.get_table_names():
                if t == main_table:
                    continue
                fks = inspector.get_foreign_keys(t)
                for fk in fks:
                    if fk['referred_table'] == main_table:
                        fk_col = fk['constrained_columns'][0]
                        del_sql = f'DELETE FROM "{t}" WHERE "{fk_col}" = :key_val'
                        connection.execute(text(del_sql), {'key_val': card_key})
            # Удаляем из основной таблицы
            del_sql = f'DELETE FROM "{main_table}" WHERE "{key_col}" = :key_val'
            connection.execute(text(del_sql), {'key_val': card_key})
        flash('Карточка и все связанные данные удалены', 'success')
        return redirect(url_for('index', card=card_name))
    
    @app.route('/button_query', methods=['GET', 'POST'])
    def button_query():
        # Получаем индексы карточки и кнопки
        row_idx = int(request.args.get('row', 0))
        fig_idx = int(request.args.get('fig', 0))
        card_template = load_card_template(card)
        table_names = inspector.get_table_names()
        data = []
        if table_names:
            needed = set()
            used_tables = []
            import re
            for fig in card_template:
                db_col = fig.get('db_column')
                db_table = fig.get('db_table')
                if db_col and db_table and db_col not in (None, '', 'None') and db_table not in (None, '', 'None'):
                    needed.add((db_table, db_col))
                    if db_table not in used_tables:
                        used_tables.append(db_table)
                if fig.get('formula'):
                    for m in re.findall(r'\{([\w\.]+)\}', fig['formula']):
                        if '.' in m:
                            t, c = m.split('.', 1)
                            needed.add((t, c))
                            if t not in used_tables:
                                used_tables.append(t)
                        else:
                            for t in table_names:
                                columns = inspector.get_columns(t)
                                if m in [col['name'] for col in columns]:
                                    needed.add((t, m))
                                    if t not in used_tables:
                                        used_tables.append(t)
            # --- Получаем данные ---
            with engine.connect() as connection:
                # Собираем SELECT с нужными JOIN
                main_table = used_tables[0]
                # Формируем alias_map
                alias_map = {main_table: 't0'}
                join_sql = ''
                fks = inspector.get_foreign_keys(main_table)
                for i, fk in enumerate(fks):
                    ref_table = fk['referred_table']
                    alias = f't{i+1}'
                    alias_map[ref_table] = alias
                    join_sql += f' LEFT JOIN "{ref_table}" {alias} ON t0."{fk["constrained_columns"][0]}" = {alias}."{fk["referred_columns"][0]}"'
                # SELECT с alias
                select_cols = []
                for t, c in needed:
                    alias = alias_map.get(t, 't0')
                    select_cols.append(f'{alias}."{c}" AS "{t}.{c}"')
                sql = f'SELECT {', '.join(select_cols)} FROM "{main_table}" t0{join_sql}'
                result = connection.execute(text(sql))
                data = list(result.mappings())
        # --- Находим нужную строку и кнопку ---
        if row_idx >= len(data):
            return '<div class="alert alert-danger">Строка не найдена</div>'
        row = data[row_idx]
        # fig_idx — это индекс фигуры в шаблоне
        if fig_idx >= len(card_template) or card_template[fig_idx].get('type') != 'ButtonFigure':
            return '<div class="alert alert-danger">Кнопка не найдена</div>'
        fig = card_template[fig_idx]
        # --- Получаем параметры кнопки ---
        table = fig.get('table')
        columns = fig.get('columns', [])
        filters = fig.get('filters', [])
        # --- Формируем SQL-запрос ---
        if not table or not columns:
            return '<div class="alert alert-warning">Выберите таблицу и столбцы для запроса.</div>'
        # --- Формируем alias для таблиц ---
        alias_map = {table: 't0'}
        join_sql = ''
        fks = inspector.get_foreign_keys(table)
        for i, fk in enumerate(fks):
            ref_table = fk['referred_table']
            alias = f't{i+1}'
            alias_map[ref_table] = alias
            join_sql += f' LEFT JOIN "{ref_table}" {alias} ON t0."{fk["constrained_columns"][0]}" = {alias}."{fk["referred_columns"][0]}"'
        # --- SELECT с универсальными псевдонимами ---
        select_cols = []
        col_labels = []
        for c in columns:
            if isinstance(c, dict):
                col_name = c['column']
                label = c.get('label', c['column'].split('.')[-1])
            else:
                col_name = c
                label = c.split('.')[-1]
            col_labels.append(label)
            if '.' in col_name:
                t, col = col_name.split('.', 1)
                alias = alias_map.get(t, 't0')
                select_cols.append(f'{alias}."{col}" AS "{t}.{col}"')
            else:
                select_cols.append(f't0."{col_name}" AS "{table}.{col_name}"')
        sql = f'SELECT {', '.join(select_cols)} FROM "{table}" t0{join_sql}'
        where = []
        params = {}
        for i, f in enumerate(filters):
            col_f = f['column'] if isinstance(f['column'], str) else f['column'].get('column', '')
            val = f['value']
            # Подстановка значения из карточки
            if isinstance(val, str) and val.startswith('{') and val.endswith('}'):
                key = val[1:-1]
                val = row.get(key)
            if '.' in col_f:
                t, col = col_f.split('.', 1)
                alias = alias_map.get(t, 't0')
                where.append(f'{alias}."{col}" {f["op"]} :val{i}')
            else:
                where.append(f't0."{col_f}" {f["op"]} :val{i}')
            params[f'val{i}'] = val
        if where:
            sql += ' WHERE ' + ' AND '.join(where)
        rows = []
        try:
            with engine.connect() as connection:
                result = connection.execute(text(sql), params)
                rows = list(result.mappings())
        except Exception as e:
            return f'<div class="alert alert-danger">Ошибка SQL: {e}</div>'
        # --- Только таблица результата ---
        if rows:
            html = '<div class="table-responsive mt-3"><table class="table table-bordered table-sm"><thead><tr>'
            for label in col_labels:
                html += f'<th>{label}</th>'
            html += '</tr></thead><tbody>'
            for r in rows:
                html += '<tr>' + ''.join([f'<td>{r[c["column"]] if isinstance(c, dict) else r[c]}</td>' for c in columns]) + '</tr>'
            html += '</tbody></table></div>'
        else:
            html = '<div class="alert alert-info mt-3">Нет данных</div>'
        return html
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Обработчик ошибки 404"""
        return render_template('error.html', error=error), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Обработчик ошибки 500"""
        return render_template('error.html', error=error), 500
    
    # Запускаем приложение
    logger.info(f"Запуск веб-сервера на порту {web_port}")
    logger.info(f"Подключение к базе данных: {connection_string.replace(password, '****')}")
    
    app.run(host="0.0.0.0", port=web_port, debug=debug)
    
    return app 

def create_module_file(modul_command: str):
    """
    Создаёт файл module2.py, module3.py или module4.py в текущей директории с соответствующим кодом.
    modul_command: строка вида 'modul(2)', 'modul(3)', 'modul(4)'
    """
    import pathlib
    import shutil
    import sys

    mapping = {
        'modul(2)': 'module2.py',
        'modul(3)': 'module3.py',
        'modul(4)': 'module4.py',
    }
    code_map = {
        'module2.py': '''import psycopg2\nimport tkinter as tk\nfrom tkinter import ttk\nfrom PIL import Image, ImageTk\nfrom tkinter import messagebox\n\ndef calculate_discount(total_sales):\n    if total_sales < 10000:\n        return "0%"\n    elif total_sales < 50000:\n        return "5%"\n    elif total_sales < 300000:\n        return "10%"\n    else:\n        return "15%"\n\ndef load_partners():\n    conn = psycopg2.connect(\n        dbname='amm',\n        user='postgres',\n        password='postgres',\n        host='localhost',  # или другой адрес сервера\n        port='5432'        # стандартный порт PostgreSQL\n    )\n    cursor = conn.cursor()\n    cursor.execute("""\n        SELECT\n            p.partner_name, p.partner_type, p.director, p.phone, p.rating,\n            COALESCE(SUM(pp.product_kolvo), 0) AS total_sales\n        FROM\n            partners p\n        LEFT JOIN\n            partner_products pp ON p.partner_name = pp.partner_name\n        GROUP BY\n            p.partner_name\n        ORDER BY\n            p.partner_name\n    """)\n    partners = cursor.fetchall()\n    conn.close()\n    return partners\n\ndef show_partners():\n    # Очищаем старые карточки, если они есть\n    for widget in cards_frame.winfo_children():\n        widget.destroy()\n    partners = load_partners()\n    for partner in partners:\n        partner_name, partner_type, director, phone, rating, total_sales = partner\n        discount = calculate_discount(total_sales)\n\n        card = tk.Frame(cards_frame, bd=1, relief=tk.SOLID, padx=10, pady=10)\n        card.pack(fill=tk.X, padx=10, pady=10)\n\n        # Верхняя строка: Тип | Имя партнера и скидка справа\n        top_frame = tk.Frame(card)\n        top_frame.pack(fill=tk.X)\n        left_label = tk.Label(top_frame, text=f"{partner_type} | {partner_name}", font=("Arial", 14))\n        left_label.pack(side=tk.LEFT, anchor="w")\n        right_label = tk.Label(top_frame, text=discount, font=("Arial", 14))\n        right_label.pack(side=tk.RIGHT, anchor="e")\n\n        # Остальная информация\n        info_label = tk.Label(card, text=f"Директор {director}\n{phone}\nРейтинг: {rating}", anchor="w", justify="left")\n        info_label.pack(anchor="w", pady=(5, 0))\n\nroot = tk.Tk()\nroot.title("Учет партнеров")\ntry:\n    logo = Image.open("Мастер пол.png")\n    logo = logo.resize((100, 100), Image.Resampling.LANCZOS)\n    logo = ImageTk.PhotoImage(logo)\n    root.iconphoto(True, logo)\nexcept:\n    messagebox.showerror("Ошибка", "Не удалось загрузить логотип")\n# cards_frame для карточек\ncards_frame = tk.Frame(root)\ncards_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)\n\nshow_partners()\n\nroot.mainloop()\n''',
        'module3.py': '''import psycopg2\nimport tkinter as tk\nfrom tkinter import ttk, messagebox\nfrom PIL import Image, ImageTk\nimport re\nimport os\n\n# Стили\nSTYLES = {\n    'bg': '#FFFFFF',\n    'secondary_bg': '#F4E8D3',\n    'accent': '#67BA80',\n    'font': 'Segoe UI'\n}\n\ndef calculate_discount(total_sales):\n    if total_sales < 10000:\n        return "0%"\n    elif total_sales < 50000:\n        return "5%"\n    elif total_sales < 300000:\n        return "10%"\n    else:\n        return "15%"\n\ndef get_db():\n    try:\n        return psycopg2.connect(\n            dbname='amm',\n            user='postgres',\n            password='postgres',\n            host='localhost',\n            port='5432'\n        )\n    except psycopg2.Error as e:\n        messagebox.showerror("Ошибка", f"Ошибка подключения к БД:\n{str(e)}")\n        return None\n\ndef load_partners():\n    conn = get_db()\n    if not conn:\n        return []\n    \n    try:\n        cursor = conn.cursor()\n        cursor.execute("""\n            SELECT p.*, COALESCE(SUM(pp.product_kolvo), 0) as total_sales\n            FROM partners p\n            LEFT JOIN partner_products pp ON p.partner_name = pp.partner_name\n            GROUP BY p.partner_name\n            ORDER BY p.partner_name\n        """)\n        return cursor.fetchall()\n    except psycopg2.Error as e:\n        messagebox.showerror("Ошибка", f"Ошибка загрузки данных:\n{str(e)}")\n        return []\n    finally:\n        conn.close()\n\nclass PartnerForm(tk.Toplevel):\n    def __init__(self, parent, partner=None):\n        super().__init__(parent)\n        self.title("Добавление партнера" if not partner else "Редактирование партнера")\n        self.geometry("500x400")\n        self.configure(bg=STYLES['bg'])\n        \n        # Поля формы\n        fields = [\n            ("Наименование", "name"),\n            ("Тип партнера", "partner_type"),\n            ("ФИО директора", "director"),\n            ("Email", "email"),\n            ("Телефон", "phone"),\n            ("Адрес", "address"),\n            ("ИНН", "inn"),\n            ("Рейтинг", "rating")\n        ]\n        self.field_order = [f[1] for f in fields]\n        \n        # Создаем поля ввода\n        self.entries = {}\n        for label, field in fields:\n            frame = tk.Frame(self, bg=STYLES['bg'])\n            frame.pack(fill=tk.X, padx=20, pady=5)\n            \n            tk.Label(frame, text=label + ":", bg=STYLES['bg'], font=(STYLES['font'], 10)).pack(side=tk.LEFT)\n            \n            if field == "partner_type":\n                self.entries[field] = ttk.Combobox(frame, values=["OOO", "АОА", "ЗАО", "ПАО"])\n            else:\n                self.entries[field] = tk.Entry(frame)\n            self.entries[field].pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)\n        \n        # Кнопки\n        btn_frame = tk.Frame(self, bg=STYLES['bg'])\n        btn_frame.pack(fill=tk.X, padx=20, pady=20)\n        \n        tk.Button(btn_frame, text="Сохранить", command=self.save,\n                 bg=STYLES['accent'], fg='white').pack(side=tk.RIGHT, padx=5)\n        tk.Button(btn_frame, text="Отмена", command=self.destroy,\n                 bg=STYLES['secondary_bg']).pack(side=tk.RIGHT, padx=5)\n        \n        # Заполняем форму данными, если они есть\n        if partner:\n            for field, value in zip(self.field_order, partner):\n                self.entries[field].delete(0, tk.END)\n                self.entries[field].insert(0, value)\n    \n    def save(self):\n        # Проверяем обязательные поля\n        if not all(self.entries[field].get().strip() for field in ['name', 'partner_type', 'rating']):\n            messagebox.showerror("Ошибка", "Заполните все обязательные поля")\n            return\n        try:\n            rating = int(self.entries['rating'].get())\n            if rating <= 0:\n                raise ValueError()\n        except ValueError:\n            messagebox.showerror("Ошибка", "Рейтинг должен быть положительным числом")\n            return\n        conn = get_db()\n        if not conn:\n            return\n        try:\n            cursor = conn.cursor()\n            # Формируем data в нужном порядке\n            data = [self.entries[field].get().strip() for field in self.field_order]\n            data[-1] = int(data[-1])  # Рейтинг\n            cursor.execute("""\n                INSERT INTO partners \n                (partner_name, partner_type, director, email, phone, address, inn, rating)\n                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)\n                ON CONFLICT (partner_name) DO UPDATE\n                SET partner_type = EXCLUDED.partner_type,\n                    director = EXCLUDED.director,\n                    email = EXCLUDED.email,\n                    phone = EXCLUDED.phone,\n                    address = EXCLUDED.address,\n                    inn = EXCLUDED.inn,\n                    rating = EXCLUDED.rating\n            """, data)\n            conn.commit()\n            messagebox.showinfo("Успех", "Данные сохранены")\n            self.master.refresh_partners()\n            self.destroy()\n        except psycopg2.Error as e:\n            messagebox.showerror("Ошибка", f"Ошибка сохранения:\n{str(e)}")\n        finally:\n            conn.close()\n\nclass MainApp(tk.Tk):\n    def __init__(self):\n        super().__init__()\n        self.title("Учет партнеров")\n        self.geometry("800x600")\n        self.configure(bg=STYLES['bg'])\n        \n        # Загружаем логотип\n        try:\n            logo = Image.open("logo.png")\n            logo = logo.resize((200, 100), Image.Resampling.LANCZOS)\n            self.logo = ImageTk.PhotoImage(logo)\n            tk.Label(self, image=self.logo, bg=STYLES['bg']).pack(pady=10)\n        except:\n            messagebox.showerror("Ошибка", "Не удалось загрузить логотип")\n        \n        # Кнопки управления\n        btn_frame = tk.Frame(self, bg=STYLES['bg'])\n        btn_frame.pack(fill=tk.X, padx=10, pady=5)\n        \n        tk.Button(btn_frame, text="Добавить партнера",\n                 command=self.add_partner,\n                 bg=STYLES['accent'], fg='white').pack(side=tk.LEFT, padx=5)\n        \n        tk.Button(btn_frame, text="Обновить",\n                 command=self.refresh_partners,\n                 bg=STYLES['secondary_bg']).pack(side=tk.LEFT, padx=5)\n        \n        # Фрейм для карточек\n        self.cards_frame = tk.Frame(self, bg=STYLES['bg'])\n        self.cards_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)\n        \n        self.refresh_partners()\n    \n    def refresh_partners(self):\n        for widget in self.cards_frame.winfo_children():\n            widget.destroy()\n        for partner in load_partners():\n            card = tk.Frame(self.cards_frame, bd=1, relief=tk.SOLID, padx=10, pady=10, bg=STYLES['bg'])\n            card.pack(fill=tk.X, padx=10, pady=5)\n            card.bind('<Button-1>', lambda e, p=partner: self.edit_partner(p))\n            top_frame = tk.Frame(card, bg=STYLES['bg'])\n            top_frame.pack(fill=tk.X)\n            header = f"{partner[1]} | {partner[0]}"\n            tk.Label(top_frame, text=header, font=(STYLES['font'], 12, 'bold'), bg=STYLES['bg']).pack(side=tk.LEFT, anchor='w')\n            discount = calculate_discount(partner[-1])\n            tk.Label(top_frame, text=discount, font=(STYLES['font'], 12), bg=STYLES['bg']).pack(side=tk.RIGHT, anchor='e')\n            info = f"{partner[2]}\n+7 {partner[4]}\nРейтинг: {partner[7]}"\n            tk.Label(card, text=info, anchor='w', justify='left', font=(STYLES['font'], 10), bg=STYLES['bg']).pack(anchor='w', pady=5)\n    \n    def add_partner(self):\n        PartnerForm(self)\n    \n    def edit_partner(self, partner):\n        PartnerForm(self, partner)\n\nif __name__ == "__main__":\n    app = MainApp()\n    app.mainloop()\n''',
        'module4.py': '''import psycopg2\nimport tkinter as tk\nfrom tkinter import ttk, messagebox\nfrom PIL import Image, ImageTk\nimport re\nimport os\n\n# Стили\nSTYLES = {\n    'bg': '#FFFFFF',\n    'secondary_bg': '#F4E8D3',\n    'accent': '#67BA80',\n    'font': 'Segoe UI'\n}\n\ndef calculate_discount(total_sales):\n    if total_sales < 10000:\n        return "0%"\n    elif total_sales < 50000:\n        return "5%"\n    elif total_sales < 300000:\n        return "10%"\n    else:\n        return "15%"\n\ndef get_db():\n    try:\n        return psycopg2.connect(\n            dbname='amm',\n            user='postgres',\n            password='postgres',\n            host='localhost',\n            port='5432'\n        )\n    except psycopg2.Error as e:\n        messagebox.showerror("Ошибка", f"Ошибка подключения к БД:\n{str(e)}")\n        return None\n\ndef load_partners():\n    conn = get_db()\n    if not conn:\n        return []\n    \n    try:\n        cursor = conn.cursor()\n        cursor.execute("""\n            SELECT p.*, COALESCE(SUM(pp.product_kolvo), 0) as total_sales\n            FROM partners p\n            LEFT JOIN partner_products pp ON p.partner_name = pp.partner_name\n            GROUP BY p.partner_name\n            ORDER BY p.partner_name\n        """)\n        return cursor.fetchall()\n    except psycopg2.Error as e:\n        messagebox.showerror("Ошибка", f"Ошибка загрузки данных:\n{str(e)}")\n        return []\n    finally:\n        conn.close()\n\nclass PartnerForm(tk.Toplevel):\n    def __init__(self, parent, partner=None):\n        super().__init__(parent)\n        self.title("Добавление партнера" if not partner else "Редактирование партнера")\n        self.geometry("500x400")\n        self.configure(bg=STYLES['bg'])\n        \n        # Поля формы\n        fields = [\n            ("Наименование", "name"),\n            ("Тип партнера", "partner_type"),\n            ("ФИО директора", "director"),\n            ("Email", "email"),\n            ("Телефон", "phone"),\n            ("Адрес", "address"),\n            ("ИНН", "inn"),\n            ("Рейтинг", "rating")\n        ]\n        self.field_order = [f[1] for f in fields]\n        \n        # Создаем поля ввода\n        self.entries = {}\n        for label, field in fields:\n            frame = tk.Frame(self, bg=STYLES['bg'])\n            frame.pack(fill=tk.X, padx=20, pady=5)\n            \n            tk.Label(frame, text=label + ":", bg=STYLES['bg'], font=(STYLES['font'], 10)).pack(side=tk.LEFT)\n            \n            if field == "partner_type":\n                self.entries[field] = ttk.Combobox(frame, values=["OOO", "АОА", "ЗАО", "ПАО"])\n            else:\n                self.entries[field] = tk.Entry(frame)\n            self.entries[field].pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)\n        \n        # Кнопки\n        btn_frame = tk.Frame(self, bg=STYLES['bg'])\n        btn_frame.pack(fill=tk.X, padx=20, pady=20)\n        \n        tk.Button(btn_frame, text="Сохранить", command=self.save,\n                 bg=STYLES['accent'], fg='white').pack(side=tk.RIGHT, padx=5)\n        tk.Button(btn_frame, text="Отмена", command=self.destroy,\n                 bg=STYLES['secondary_bg']).pack(side=tk.RIGHT, padx=5)\n        \n        # Заполняем форму данными, если они есть\n        if partner:\n            for field, value in zip(self.field_order, partner):\n                self.entries[field].delete(0, tk.END)\n                self.entries[field].insert(0, value)\n    \n    def save(self):\n        # Проверяем обязательные поля\n        if not all(self.entries[field].get().strip() for field in ['name', 'partner_type', 'rating']):\n            messagebox.showerror("Ошибка", "Заполните все обязательные поля")\n            return\n        try:\n            rating = int(self.entries['rating'].get())\n            if rating <= 0:\n                raise ValueError()\n        except ValueError:\n            messagebox.showerror("Ошибка", "Рейтинг должен быть положительным числом")\n            return\n        conn = get_db()\n        if not conn:\n            return\n        try:\n            cursor = conn.cursor()\n            # Формируем data в нужном порядке\n            data = [self.entries[field].get().strip() for field in self.field_order]\n            data[-1] = int(data[-1])  # Рейтинг\n            cursor.execute("""\n                INSERT INTO partners \n                (partner_name, partner_type, director, email, phone, address, inn, rating)\n                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)\n                ON CONFLICT (partner_name) DO UPDATE\n                SET partner_type = EXCLUDED.partner_type,\n                    director = EXCLUDED.director,\n                    email = EXCLUDED.email,\n                    phone = EXCLUDED.phone,\n                    address = EXCLUDED.address,\n                    inn = EXCLUDED.inn,\n                    rating = EXCLUDED.rating\n            """, data)\n            conn.commit()\n            messagebox.showinfo("Успех", "Данные сохранены")\n            self.master.refresh_partners()\n            self.destroy()\n        except psycopg2.Error as e:\n            messagebox.showerror("Ошибка", f"Ошибка сохранения:\n{str(e)}")\n        finally:\n            conn.close()\n\nclass ProductHistoryWindow(tk.Toplevel):\n    def __init__(self, parent, partner_name):\n        super().__init__(parent)\n        self.title(f"История реализации - {partner_name}")\n        self.geometry("800x600")\n        self.configure(bg=STYLES['bg'])\n        \n        # Заголовок\n        header_frame = tk.Frame(self, bg=STYLES['bg'])\n        header_frame.pack(fill=tk.X, padx=20, pady=10)\n        tk.Label(header_frame, text=f"История реализации продукции партнера: {partner_name}",\n                font=(STYLES['font'], 14, 'bold'), bg=STYLES['bg']).pack()\n        \n        # Таблица\n        columns = ("product_name", "quantity", "date_of_sale")\n        self.tree = ttk.Treeview(self, columns=columns, show="headings")\n        \n        # Настройка заголовков\n        self.tree.heading("product_name", text="Наименование продукции")\n        self.tree.heading("quantity", text="Количество")\n        self.tree.heading("date_of_sale", text="Дата продажи")\n        \n        \n        # Размещаем таблицу и скроллбар\n        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)\n        \n        # Загружаем данные\n        self.load_history(partner_name)\n    \n    def load_history(self, partner_name):\n        conn = get_db()\n        if not conn:\n            return\n        \n        try:\n            cursor = conn.cursor()\n            cursor.execute("""\n                SELECT product_name, product_kolvo, date_of_sale\n                FROM partner_products\n                WHERE partner_name = %s\n                ORDER BY date_of_sale DESC\n            """, (partner_name,))\n            \n            # Очищаем существующие данные\n            for item in self.tree.get_children():\n                self.tree.delete(item)\n            \n            # Добавляем новые данные\n            for row in cursor.fetchall():\n                self.tree.insert("", tk.END, values=row)\n                \n        except psycopg2.Error as e:\n            messagebox.showerror("Ошибка", f"Ошибка загрузки истории:\n{str(e)}")\n        finally:\n            conn.close()\n\ndef calculate_material_quantity(product_type, material_id, product_quantity, param1, param2):\n    # Проверка входных параметров\n    if any(x <= 0 for x in [param1, param2, product_quantity]):\n        return -1\n        \n    try:\n        conn = get_db()\n        if not conn:\n            return -1\n            \n        cursor = conn.cursor()\n        \n        # Получаем коэффициенты из БД по обновленным именам колонок\n        cursor.execute("""\n            SELECT \n                (SELECT koef_product_type FROM product_types WHERE product_type = %s),\n                (SELECT percent_braka FROM material_type WHERE material_id = %s)\n        """, (product_type, material_id))\n        \n        result = cursor.fetchone()\n        if not result or None in result:\n            return -1\n            \n        # Используем более понятные имена для коэффициентов в коде\n        product_coefficient, defect_percentage = result\n        \n        # Расчет количества материала\n        material_per_unit = param1 * param2 * product_coefficient\n        total_material = material_per_unit * product_quantity * (1 + defect_percentage / 100)\n        \n        return int(total_material) + 1\n        \n    except (psycopg2.Error, ValueError, TypeError):\n        return -1\n    finally:\n        if conn:\n            conn.close()\n\nclass MainApp(tk.Tk):\n    def __init__(self):\n        super().__init__()\n        self.title("Учет партнеров")\n        self.geometry("800x600")\n        self.configure(bg=STYLES['bg'])\n        \n        # Загружаем логотип\n        try:\n            logo = Image.open("Мастер пол.png")\n            logo = logo.resize((100, 100), Image.Resampling.LANCZOS)\n            self.logo = ImageTk.PhotoImage(logo)\n            self.iconphoto(True, self.logo)\n        except:\n            messagebox.showerror("Ошибка", "Не удалось загрузить логотип")\n        \n        # Кнопки управления\n        btn_frame = tk.Frame(self, bg=STYLES['bg'])\n        btn_frame.pack(fill=tk.X, padx=10, pady=5)\n        \n        tk.Button(btn_frame, text="Добавить партнера",\n                 command=self.add_partner,\n                 bg=STYLES['accent'], fg='white').pack(side=tk.LEFT, padx=5)\n        \n        tk.Button(btn_frame, text="Обновить",\n                 command=self.refresh_partners,\n                 bg=STYLES['secondary_bg']).pack(side=tk.LEFT, padx=5)\n        \n        tk.Button(btn_frame, text="Расчет материала",\n                 command=None,\n                 bg=STYLES['accent'], fg='white').pack(side=tk.LEFT, padx=5)\n        \n        # Фрейм для карточек\n        self.cards_frame = tk.Frame(self, bg=STYLES['bg'])\n        self.cards_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)\n        \n        self.refresh_partners()\n    \n    def refresh_partners(self):\n        for widget in self.cards_frame.winfo_children():\n            widget.destroy()\n        for partner in load_partners():\n            card = tk.Frame(self.cards_frame, bd=1, relief=tk.SOLID, padx=10, pady=10, bg=STYLES['bg'])\n            card.pack(fill=tk.X, padx=10, pady=5)\n            card.bind('<Button-1>', lambda e, p=partner: self.edit_partner(p))\n            \n            top_frame = tk.Frame(card, bg=STYLES['bg'])\n            top_frame.pack(fill=tk.X)\n            \n            header = f"{partner[1]} | {partner[0]}"\n            tk.Label(top_frame, text=header, font=(STYLES['font'], 12, 'bold'), bg=STYLES['bg']).pack(side=tk.LEFT, anchor='w')\n            \n            # Добавляем кнопку истории\n            history_btn = tk.Button(top_frame, text="История", \n                                  command=lambda p=partner: self.show_product_history(p),\n                                  bg=STYLES['accent'], fg='white')\n            history_btn.pack(side=tk.RIGHT, padx=5)\n            \n            discount = calculate_discount(partner[-1])\n            tk.Label(top_frame, text=discount, font=(STYLES['font'], 12), bg=STYLES['bg']).pack(side=tk.RIGHT, padx=5)\n            \n            info = f"{partner[2]}\n+7 {partner[4]}\nРейтинг: {partner[7]}"\n            tk.Label(card, text=info, justify='left', font=(STYLES['font'], 10), bg=STYLES['bg']).pack(anchor='w', pady=5)\n    \n    def add_partner(self):\n        PartnerForm(self)\n    \n    def edit_partner(self, partner):\n        PartnerForm(self, partner)\n\n    def show_product_history(self, partner):\n        ProductHistoryWindow(self, partner[0])\n\nif __name__ == "__main__":\n    app = MainApp()\n    app.mainloop()\n''',
    }
    
    filename = mapping.get(modul_command)
    if not filename:
        raise ValueError("modul_command должен быть 'modul(2)', 'modul(3)' или 'modul(4)'")
    code = code_map[filename]
    path = pathlib.Path.cwd() / filename
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    return str(path) 

# --- TKINTER CARD DESIGNER ---
def tkinter_card_designer():
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    import os
    import json

    class CardDesigner(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("Конструктор карточек PGAdmin Site")
            self.geometry("800x600")
            self.configure(bg="#f8f9fa")
            self.fields = []
            self.card_name = tk.StringVar()
            self.card_fields_frame = tk.Frame(self, bg="#f8f9fa")
            self.card_fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            self._draw_ui()

        def _draw_ui(self):
            top = tk.Frame(self, bg="#f8f9fa")
            top.pack(fill=tk.X, padx=20, pady=10)
            tk.Label(top, text="Название шаблона:", bg="#f8f9fa").pack(side=tk.LEFT)
            tk.Entry(top, textvariable=self.card_name, width=30).pack(side=tk.LEFT, padx=5)
            tk.Button(top, text="Добавить поле", command=self.add_field, bg="#67BA80", fg="white").pack(side=tk.LEFT, padx=10)
            tk.Button(top, text="Сохранить шаблон", command=self.save_card, bg="#007bff", fg="white").pack(side=tk.LEFT, padx=10)
            self.fields_container = tk.Frame(self.card_fields_frame, bg="#f8f9fa")
            self.fields_container.pack(fill=tk.BOTH, expand=True)
            self.refresh_fields()

        def add_field(self):
            field = {"label": tk.StringVar(), "type": tk.StringVar(value="text"), "calc": tk.StringVar()}
            self.fields.append(field)
            self.refresh_fields()

        def remove_field(self, idx):
            del self.fields[idx]
            self.refresh_fields()

        def refresh_fields(self):
            for widget in self.fields_container.winfo_children():
                widget.destroy()
            for idx, field in enumerate(self.fields):
                row = tk.Frame(self.fields_container, bg="#f8f9fa")
                row.pack(fill=tk.X, pady=3)
                tk.Label(row, text=f"Поле {idx+1}:", bg="#f8f9fa").pack(side=tk.LEFT)
                tk.Entry(row, textvariable=field["label"], width=20).pack(side=tk.LEFT, padx=5)
                ttk.Combobox(row, textvariable=field["type"], values=["text", "number", "discount_calc"], width=12).pack(side=tk.LEFT, padx=5)
                tk.Entry(row, textvariable=field["calc"], width=30).pack(side=tk.LEFT, padx=5)
                tk.Label(row, text="(формула/выражение, если нужно)", bg="#f8f9fa").pack(side=tk.LEFT, padx=2)
                tk.Button(row, text="Удалить", command=lambda i=idx: self.remove_field(i), bg="#dc3545", fg="white").pack(side=tk.LEFT, padx=5)

        def save_card(self):
            name = self.card_name.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Введите название шаблона!")
                return
            if not self.fields:
                messagebox.showerror("Ошибка", "Добавьте хотя бы одно поле!")
                return
            card_data = []
            for f in self.fields:
                card_data.append({
                    "label": f["label"].get(),
                    "type": f["type"].get(),
                    "calc": f["calc"].get()
                })
            os.makedirs(os.path.join(os.path.dirname(__file__), "templates", "cards"), exist_ok=True)
            path = os.path.join(os.path.dirname(__file__), "templates", "cards", f"{name}.json")
            with open(path, "w", encoding="utf-8") as fp:
                json.dump(card_data, fp, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", f"Шаблон '{name}' сохранён!")

    CardDesigner().mainloop() 