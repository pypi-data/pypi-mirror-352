import tkinter as tk
from tkinter import colorchooser, simpledialog, ttk, filedialog, messagebox
import json
import sqlalchemy
import tkinter.font as tkfont

class Figure:
    def __init__(self, x1, y1, x2, y2, fill='#ffffff', outline='#000000', width=2):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.fill = fill
        self.outline = outline
        self.width = width
        self.selected = False
    def draw(self, canvas):
        pass
    def contains(self, x, y):
        return False
    def move(self, dx, dy):
        self.x1 += dx
        self.x2 += dx
        self.y1 += dy
        self.y2 += dy
    def resize(self, x2, y2):
        self.x2 = x2
        self.y2 = y2

class Rectangle(Figure):
    def draw(self, canvas):
        dash = (4, 2) if self.selected else None
        return canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill=self.fill, outline=self.outline, width=self.width, dash=dash)
    def contains(self, x, y):
        return min(self.x1, self.x2) <= x <= max(self.x1, self.x2) and min(self.y1, self.y2) <= y <= max(self.y1, self.y2)

class Ellipse(Figure):
    def draw(self, canvas):
        dash = (4, 2) if self.selected else None
        return canvas.create_oval(self.x1, self.y1, self.x2, self.y2, fill=self.fill, outline=self.outline, width=self.width, dash=dash)
    def contains(self, x, y):
        rx = abs(self.x2 - self.x1) / 2
        ry = abs(self.y2 - self.y1) / 2
        cx = (self.x1 + self.x2) / 2
        cy = (self.y1 + self.y2) / 2
        if rx == 0 or ry == 0:
            return False
        return ((x - cx) ** 2) / (rx ** 2) + ((y - cy) ** 2) / (ry ** 2) <= 1

class Line(Figure):
    def draw(self, canvas):
        dash = (4, 2) if self.selected else None
        return canvas.create_line(self.x1, self.y1, self.x2, self.y2, fill=self.outline, width=self.width, dash=dash)
    def contains(self, x, y):
        # Простая проверка близости к линии
        from math import hypot
        dist = abs((self.y2 - self.y1)*x - (self.x2 - self.x1)*y + self.x2*self.y1 - self.y2*self.x1) / max(1, ((self.y2 - self.y1)**2 + (self.x2 - self.x1)**2) ** 0.5)
        return dist < 8

class Text(Figure):
    def __init__(self, x1, y1, x2, y2, text='Текст', fill='#000000', font_size=14, formula=None, db_column=None, db_table=None, font_family='Segoe UI'):
        super().__init__(x1, y1, x2, y2, fill='', outline='', width=0)
        self.text = text
        self.font_size = font_size
        self.text_color = fill
        self.formula = formula
        self.db_column = db_column
        self.db_table = db_table
        self.font_family = font_family
    def draw(self, canvas):
        dash = (4, 2) if self.selected else None
        return canvas.create_text((self.x1+self.x2)//2, (self.y1+self.y2)//2, text=self.text, fill=self.text_color, font=("Segoe UI", self.font_size, "bold" if self.selected else "normal"))
    def contains(self, x, y):
        return min(self.x1, self.x2)-10 <= x <= max(self.x1, self.x2)+10 and min(self.y1, self.y2)-10 <= y <= max(self.y1, self.y2)+10
    def move(self, dx, dy):
        self.x1 += dx
        self.x2 += dx
        self.y1 += dy
        self.y2 += dy
    def resize(self, x2, y2):
        self.x2 = x2
        self.y2 = y2

class ButtonFigure(Figure):
    def __init__(self, x1, y1, x2, y2, text='Кнопка', fill='#007bff', outline='#0056b3', width=2, shape='rect', table=None, filters=None, columns=None):
        super().__init__(x1, y1, x2, y2, fill=fill, outline=outline, width=width)
        self.text = text
        self.shape = shape  # 'rect', 'round', 'circle'
        self.table = table
        self.filters = filters or []  # [{'column': ..., 'op': ..., 'value': ...}]
        self.columns = columns or []  # список выбранных столбцов
    def draw(self, canvas):
        dash = (4, 2) if self.selected else None
        if self.shape == 'rect':
            canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill=self.fill, outline=self.outline, width=self.width, dash=dash)
        elif self.shape == 'round':
            canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill=self.fill, outline=self.outline, width=self.width, dash=dash, smooth=True)
        elif self.shape == 'circle':
            r = min(abs(self.x2-self.x1), abs(self.y2-self.y1))//2
            cx = (self.x1+self.x2)//2
            cy = (self.y1+self.y2)//2
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=self.fill, outline=self.outline, width=self.width, dash=dash)
        canvas.create_text((self.x1+self.x2)//2, (self.y1+self.y2)//2, text=self.text, fill='#fff', font=("Segoe UI", 12, "bold"))
    def contains(self, x, y):
        return min(self.x1, self.x2)-10 <= x <= max(self.x1, self.x2)+10 and min(self.y1, self.y2)-10 <= y <= max(self.y1, self.y2)+10
    def move(self, dx, dy):
        self.x1 += dx
        self.x2 += dx
        self.y1 += dy
        self.y2 += dy
    def resize(self, x2, y2):
        self.x2 = x2
        self.y2 = y2

class CardEditor(tk.Tk):
    def __init__(self, username=None, password=None, database=None, host='localhost', port=5432):
        super().__init__()
        self.title("Редактор карточек (панель свойств + drag&drop)")
        self.geometry("1200x800")
        self.figures = []
        self.selected = None
        self.mode = None
        self.start_x = self.start_y = 0
        self.db_columns = []
        self.db_tables = []
        self.db_connected = False
        self.db_error = None
        self.engine = None
        self.inspector = None
        self.current_table = None
        # --- Подключение к БД ---
        if username and password and database:
            try:
                conn_str = f"postgresql://{username}:{password}@{host}:{port}/{database}"
                self.engine = sqlalchemy.create_engine(conn_str)
                self.inspector = sqlalchemy.inspect(self.engine)
                self.db_tables = self.inspector.get_table_names()
                if self.db_tables:
                    self.current_table = self.db_tables[0]
                    columns = self.inspector.get_columns(self.current_table)
                    self.db_columns = [col['name'] for col in columns]
                self.db_connected = True
            except Exception as e:
                self.db_error = str(e)
                self.db_columns = ['Ошибка подключения к БД']
        else:
            self.db_columns = ['partner_name', 'partner_type', 'director', 'phone', 'rating', 'total_sales']
        self._build_ui()
        self.dragged_col = None
        self.drag_label = None

    def _build_ui(self):
        main = tk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True)
        # Левая панель: таблицы и столбцы
        left = tk.Frame(main, width=200, bg="#f4f4f4")
        left.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(left, text="Таблица:", bg="#f4f4f4", font=("Segoe UI", 11, "bold")).pack(pady=(10,2))
        # --- Combobox для выбора таблицы ---
        self.table_var = tk.StringVar(value=self.current_table if self.db_tables else None)
        self.table_combo = ttk.Combobox(left, values=self.db_tables, textvariable=self.table_var, state="readonly")
        self.table_combo.pack(fill=tk.X, padx=8)
        self.table_combo.bind('<<ComboboxSelected>>', self.on_table_change)
        tk.Label(left, text="Столбцы БД", bg="#f4f4f4", font=("Segoe UI", 12, "bold")).pack(pady=10)
        self.col_frame = tk.Frame(left, bg="#f4f4f4")
        self.col_frame.pack(fill=tk.X, padx=4)
        self.update_col_list()
        tk.Button(left, text="Сохранить шаблон", command=self.save_template, bg="#67BA80", fg="white").pack(pady=20, fill=tk.X, padx=8)
        tk.Button(left, text="Загрузить шаблон", command=self.load_template, bg="#007bff", fg="white").pack(pady=4, fill=tk.X, padx=8)
        # Центральная область: Canvas
        center = tk.Frame(main)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        toolbar = tk.Frame(center, bg="#f4f4f4")
        toolbar.pack(side=tk.TOP, fill=tk.X)
        tk.Button(toolbar, text="Прямоугольник", command=lambda: self.set_mode('rect')).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Круг", command=lambda: self.set_mode('ellipse')).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Линия", command=lambda: self.set_mode('line')).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Текст", command=lambda: self.set_mode('text')).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Кнопка", command=lambda: self.set_mode('button')).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Формула", command=self.add_formula_field).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Удалить", command=self.delete_selected).pack(side=tk.LEFT, padx=10)
        self.canvas = tk.Canvas(center, bg="#fff", highlightthickness=1, highlightbackground="#bbb")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        # Правая панель: свойства фигуры
        self.prop_panel = tk.Frame(main, width=260, bg="#f8f9fa")
        self.prop_panel.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(self.prop_panel, text="Свойства", bg="#f8f9fa", font=("Segoe UI", 12, "bold")).pack(pady=10)
        self.prop_widgets = {}
        self.update_prop_panel()

    def update_col_list(self):
        for w in self.col_frame.winfo_children():
            w.destroy()
        for col in self.db_columns:
            lbl = tk.Label(self.col_frame, text=col, bg="#e9ecef", relief=tk.RAISED, padx=5, pady=3)
            lbl.pack(fill=tk.X, padx=4, pady=2)
            lbl.bind('<ButtonPress-1>', lambda e, c=col: self.start_drag_col(e, c))
            lbl.bind('<B1-Motion>', self.drag_col_motion)
            lbl.bind('<ButtonRelease-1>', self.drop_col)

    def on_table_change(self, event=None):
        table = self.table_var.get()
        if self.db_connected and table:
            columns = self.inspector.get_columns(table)
            self.db_columns = [col['name'] for col in columns]
            self.current_table = table
            self.update_col_list()

    def set_mode(self, mode):
        self.mode = mode

    def on_click(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.mode:
            if self.mode == 'rect':
                fig = Rectangle(event.x, event.y, event.x+1, event.y+1)
            elif self.mode == 'ellipse':
                fig = Ellipse(event.x, event.y, event.x+1, event.y+1)
            elif self.mode == 'line':
                fig = Line(event.x, event.y, event.x+1, event.y+1)
            elif self.mode == 'text':
                text = simpledialog.askstring("Текст", "Введите текст:", parent=self)
                if not text:
                    return
                fig = Text(event.x, event.y, event.x+120, event.y+30, text=text)
            elif self.mode == 'button':
                text = simpledialog.askstring("Надпись на кнопке", "Введите текст:", parent=self) or 'Кнопка'
                fig = ButtonFigure(event.x, event.y, event.x+120, event.y+40, text=text)
            else:
                return
            self.figures.append(fig)
            self.selected = fig
            self.mode = None
            self.drawing_new = True
            self.redraw()
            self.update_prop_panel()
        else:
            for fig in reversed(self.figures):
                if fig.contains(event.x, event.y):
                    self.selected = fig
                    self.offset_x = event.x - fig.x1
                    self.offset_y = event.y - fig.y1
                    break
            else:
                self.selected = None
            self.redraw()
            self.update_prop_panel()

    def on_drag(self, event):
        if self.selected:
            # Гарантируем, что offset_x и offset_y определены
            if not hasattr(self, 'offset_x') or not hasattr(self, 'offset_y'):
                self.offset_x = 0
                self.offset_y = 0
            # --- Новая фигура: растягиваем ---
            if hasattr(self, 'drawing_new') and self.drawing_new:
                self.selected.resize(event.x, event.y)
            elif isinstance(self.selected, Line):
                self.selected.resize(event.x, event.y)
            elif isinstance(self.selected, Text):
                self.selected.move(event.x - self.selected.x1 - self.offset_x, event.y - self.selected.y1 - self.offset_y)
            else:
                if event.state & 0x0001:
                    self.selected.resize(event.x, event.y)
                else:
                    self.selected.move(event.x - self.selected.x1 - self.offset_x, event.y - self.selected.y1 - self.offset_y)
            self.redraw()
            self.update_prop_panel()

    def on_release(self, event):
        if hasattr(self, 'drawing_new'):
            self.drawing_new = False

    # --- Панель свойств ---
    def update_prop_panel(self):
        for w in self.prop_panel.winfo_children()[1:]:
            w.destroy()
        fig = self.selected
        if not fig:
            return
        # Цвет заливки
        if hasattr(fig, 'fill'):
            row = tk.Frame(self.prop_panel, bg="#f8f9fa")
            row.pack(fill=tk.X, pady=2, padx=8)
            tk.Label(row, text="Цвет заливки:", bg="#f8f9fa").pack(side=tk.LEFT)
            btn = tk.Button(row, bg=fig.fill or "#ffffff", width=3, command=lambda: self.choose_color(fig, 'fill'))
            btn.pack(side=tk.LEFT, padx=5)
        # Цвет обводки
        if hasattr(fig, 'outline'):
            row = tk.Frame(self.prop_panel, bg="#f8f9fa")
            row.pack(fill=tk.X, pady=2, padx=8)
            tk.Label(row, text="Цвет обводки:", bg="#f8f9fa").pack(side=tk.LEFT)
            btn = tk.Button(row, bg=fig.outline or "#000000", width=3, command=lambda: self.choose_color(fig, 'outline'))
            btn.pack(side=tk.LEFT, padx=5)
        # Толщина линии
        if hasattr(fig, 'width'):
            row = tk.Frame(self.prop_panel, bg="#f8f9fa")
            row.pack(fill=tk.X, pady=2, padx=8)
            tk.Label(row, text="Толщина:", bg="#f8f9fa").pack(side=tk.LEFT)
            spin = tk.Spinbox(row, from_=1, to=10, width=4, command=lambda: self.set_prop(fig, 'width', spin.get()))
            spin.delete(0, tk.END)
            spin.insert(0, fig.width)
            spin.pack(side=tk.LEFT, padx=5)
            spin.bind('<FocusOut>', lambda e: self.set_prop(fig, 'width', spin.get()))
        # Для текста
        if isinstance(fig, Text):
            row = tk.Frame(self.prop_panel, bg="#f8f9fa")
            row.pack(fill=tk.X, pady=2, padx=8)
            tk.Label(row, text="Текст:", bg="#f8f9fa").pack(side=tk.LEFT)
            entry = tk.Entry(row, width=18)
            entry.insert(0, fig.text)
            entry.pack(side=tk.LEFT, padx=5)
            entry.bind('<FocusOut>', lambda e: self.set_prop(fig, 'text', entry.get()))
            # Цвет текста
            row2 = tk.Frame(self.prop_panel, bg="#f8f9fa")
            row2.pack(fill=tk.X, pady=2, padx=8)
            tk.Label(row2, text="Цвет текста:", bg="#f8f9fa").pack(side=tk.LEFT)
            btn = tk.Button(row2, bg=getattr(fig, 'text_color', None) or "#000000", width=3, command=lambda: self.choose_color(fig, 'text_color'))
            btn.pack(side=tk.LEFT, padx=5)
            # Размер шрифта
            row3 = tk.Frame(self.prop_panel, bg="#f8f9fa")
            row3.pack(fill=tk.X, pady=2, padx=8)
            tk.Label(row3, text="Размер шрифта:", bg="#f8f9fa").pack(side=tk.LEFT)
            spin = tk.Spinbox(row3, from_=6, to=72, width=4, command=lambda: self.set_font_size(fig, spin))
            spin.delete(0, tk.END)
            spin.insert(0, fig.font_size)
            spin.pack(side=tk.LEFT, padx=5)
            spin.bind('<FocusOut>', lambda e: self.set_font_size(fig, spin))
            # Выбор шрифта
            row4 = tk.Frame(self.prop_panel, bg="#f8f9fa")
            row4.pack(fill=tk.X, pady=2, padx=8)
            tk.Label(row4, text="Шрифт:", bg="#f8f9fa").pack(side=tk.LEFT)
            fonts = sorted(set(tkfont.families()))
            var = tk.StringVar(value=fig.font_family)
            combo = ttk.Combobox(row4, textvariable=var, values=fonts, width=18)
            combo.pack(side=tk.LEFT, padx=5)
            def on_font_change(event=None):
                fig.font_family = var.get()
                self.redraw()
            combo.bind('<<ComboboxSelected>>', on_font_change)
            # Формула
            row5 = tk.Frame(self.prop_panel, bg="#f8f9fa")
            row5.pack(fill=tk.X, pady=2, padx=8)
            tk.Label(row5, text="Формула:", bg="#f8f9fa").pack(side=tk.LEFT)
            entry = tk.Entry(row5, width=24)
            entry.insert(0, fig.formula or "")
            entry.pack(side=tk.LEFT, padx=5)
            def on_formula_change(e=None):
                fig.formula = entry.get()
            entry.bind('<FocusOut>', on_formula_change)
            entry.bind('<Return>', on_formula_change)
        elif isinstance(fig, ButtonFigure):
            # Надпись
            row = tk.Frame(self.prop_panel, bg="#f8f9fa")
            row.pack(fill=tk.X, pady=2, padx=8)
            tk.Label(row, text="Текст на кнопке:", bg="#f8f9fa").pack(side=tk.LEFT)
            entry = tk.Entry(row, width=18)
            entry.insert(0, fig.text)
            entry.pack(side=tk.LEFT, padx=5)
            entry.bind('<FocusOut>', lambda e: self.set_prop(fig, 'text', entry.get()))
            # Цвет кнопки
            row2 = tk.Frame(self.prop_panel, bg="#f8f9fa")
            row2.pack(fill=tk.X, pady=2, padx=8)
            tk.Label(row2, text="Цвет:", bg="#f8f9fa").pack(side=tk.LEFT)
            btn = tk.Button(row2, bg=fig.fill or "#007bff", width=3, command=lambda: self.choose_color(fig, 'fill'))
            btn.pack(side=tk.LEFT, padx=5)
            # Форма
            row3 = tk.Frame(self.prop_panel, bg="#f8f9fa")
            row3.pack(fill=tk.X, pady=2, padx=8)
            tk.Label(row3, text="Форма:", bg="#f8f9fa").pack(side=tk.LEFT)
            var = tk.StringVar(value=fig.shape)
            combo = ttk.Combobox(row3, textvariable=var, values=["rect", "round", "circle"], width=10)
            combo.pack(side=tk.LEFT, padx=5)
            def on_shape_change(event=None):
                fig.shape = var.get()
                self.redraw()
            combo.bind('<<ComboboxSelected>>', on_shape_change)
            # Таблица для открытия
            row4 = tk.Frame(self.prop_panel, bg="#f8f9fa")
            row4.pack(fill=tk.X, pady=2, padx=8)
            tk.Label(row4, text="Таблица:", bg="#f8f9fa").pack(side=tk.LEFT)
            var_table = tk.StringVar(value=fig.table)
            combo_table = ttk.Combobox(row4, textvariable=var_table, values=self.db_tables, width=18)
            combo_table.pack(side=tk.LEFT, padx=5)
            def on_table_change(event=None):
                fig.table = var_table.get()
                # При смене таблицы сбрасываем выбранные столбцы и фильтры
                fig.columns = []
                fig.filters = []
                self.redraw()
                self.update_prop_panel()
            combo_table.bind('<<ComboboxSelected>>', on_table_change)
            # Столбцы для вывода
            if fig.table:
                # Основные столбцы
                col_names = [f'{fig.table}.{col["name"]}' for col in self.inspector.get_columns(fig.table)]
                # Добавляем столбцы связанных таблиц (по foreign key)
                fks = self.inspector.get_foreign_keys(fig.table)
                for fk in fks:
                    ref_table = fk['referred_table']
                    for col in self.inspector.get_columns(ref_table):
                        col_names.append(f'{ref_table}.{col["name"]}')
                row5 = tk.Frame(self.prop_panel, bg="#f8f9fa")
                row5.pack(fill=tk.X, pady=2, padx=8)
                tk.Label(row5, text="Столбцы:", bg="#f8f9fa").pack(side=tk.LEFT)
                def open_columns_dialog():
                    win = tk.Toplevel(self)
                    win.title("Выбор и настройка столбцов")
                    win.grab_set()
                    # --- Список выбранных столбцов (column, label) ---
                    selected = fig.columns or []
                    # Преобразуем старый формат (list of str) в list of dict
                    if selected and isinstance(selected[0], str):
                        selected = [{"column": c, "label": c.split('.')[-1]} for c in selected]
                    # Все доступные столбцы
                    all_cols = [f'{fig.table}.{col["name"]}' for col in self.inspector.get_columns(fig.table)]
                    fks = self.inspector.get_foreign_keys(fig.table)
                    for fk in fks:
                        ref_table = fk['referred_table']
                        for col in self.inspector.get_columns(ref_table):
                            all_cols.append(f'{ref_table}.{col["name"]}')
                    # --- UI ---
                    frame = tk.Frame(win)
                    frame.pack(fill=tk.BOTH, expand=True)
                    listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=40, height=10)
                    listbox.pack(side=tk.LEFT, fill=tk.Y, padx=4, pady=4)
                    # Отображаем выбранные столбцы
                    def refresh_listbox():
                        listbox.delete(0, tk.END)
                        for item in selected:
                            listbox.insert(tk.END, f'{item["column"]} → {item["label"]}')
                        # Обновляем доступные для добавления
                        available = [c for c in all_cols if c not in [x['column'] for x in selected]]
                        combo['values'] = available
                        if available:
                            var_col.set(available[0])
                        else:
                            var_col.set('')
                            btn_add.config(state=tk.DISABLED)
                    # Кнопки вверх/вниз
                    btns = tk.Frame(frame)
                    btns.pack(side=tk.LEFT, fill=tk.Y, padx=2)
                    def move_up():
                        idx = listbox.curselection()
                        if idx and idx[0] > 0:
                            i = idx[0]
                            selected[i-1], selected[i] = selected[i], selected[i-1]
                            refresh_listbox()
                            listbox.select_set(i-1)
                    def move_down():
                        idx = listbox.curselection()
                        if idx and idx[0] < len(selected)-1:
                            i = idx[0]
                            selected[i+1], selected[i] = selected[i], selected[i+1]
                            refresh_listbox()
                            listbox.select_set(i+1)
                    tk.Button(btns, text='↑', width=2, command=move_up).pack(pady=2)
                    tk.Button(btns, text='↓', width=2, command=move_down).pack(pady=2)
                    # Кнопка удалить
                    def delete_col():
                        idx = listbox.curselection()
                        if idx:
                            selected.pop(idx[0])
                            refresh_listbox()
                    tk.Button(btns, text='Удалить', command=delete_col).pack(pady=8)
                    # Добавление нового столбца
                    add_frame = tk.Frame(win)
                    add_frame.pack(fill=tk.X, pady=6)
                    tk.Label(add_frame, text='Столбец:').pack(side=tk.LEFT)
                    var_col = tk.StringVar()
                    combo = ttk.Combobox(add_frame, values=[], textvariable=var_col, width=24, state='readonly')
                    combo.pack(side=tk.LEFT, padx=4)
                    tk.Label(add_frame, text='Подпись:').pack(side=tk.LEFT)
                    var_label = tk.StringVar()
                    entry = tk.Entry(add_frame, textvariable=var_label, width=16)
                    entry.pack(side=tk.LEFT, padx=4)
                    def on_combo_change(event=None):
                        var_label.set(var_col.get().split('.')[-1] if var_col.get() else '')
                    combo.bind('<<ComboboxSelected>>', on_combo_change)
                    def add_col():
                        col = var_col.get()
                        label = var_label.get().strip() or col.split('.')[-1]
                        if col and not any(x['column']==col for x in selected):
                            selected.append({"column": col, "label": label})
                            refresh_listbox()
                    btn_add = tk.Button(add_frame, text='Добавить', command=add_col)
                    btn_add.pack(side=tk.LEFT, padx=4)
                    refresh_listbox()
                    # Сохранить
                    def on_ok():
                        fig.columns = selected.copy()
                        win.destroy()
                        self.redraw()
                        self.update_prop_panel()
                    tk.Button(win, text="Сохранить", command=on_ok).pack(pady=8)
                # Показываем выбранные
                lbl = tk.Label(row5, text=", ".join([x['label'] for x in (fig.columns or []) if isinstance(x, dict)]), bg="#f8f9fa", wraplength=180, justify='left')
                lbl.pack(side=tk.LEFT, padx=5)
                btn_cols = tk.Button(row5, text="Выбрать столбцы", command=open_columns_dialog)
                btn_cols.pack(side=tk.LEFT, padx=5)
            # Условия фильтрации
            if fig.table:
                row6 = tk.Frame(self.prop_panel, bg="#f8f9fa")
                row6.pack(fill=tk.X, pady=2, padx=8)
                tk.Label(row6, text="Фильтры:", bg="#f8f9fa").pack(side=tk.LEFT)
                btn_add = tk.Button(row6, text="+", command=lambda: self.add_filter(fig))
                btn_add.pack(side=tk.LEFT, padx=2)
                for i, f in enumerate(fig.filters or []):
                    rowf = tk.Frame(self.prop_panel, bg="#f8f9fa")
                    rowf.pack(fill=tk.X, pady=1, padx=16)
                    tk.Label(rowf, text=f['column'], bg="#f8f9fa").pack(side=tk.LEFT)
                    tk.Label(rowf, text=f['op'], bg="#f8f9fa").pack(side=tk.LEFT)
                    tk.Label(rowf, text=f['value'], bg="#f8f9fa").pack(side=tk.LEFT)
                    btn_del = tk.Button(rowf, text="x", command=lambda idx=i: self.del_filter(fig, idx), width=2)
                    btn_del.pack(side=tk.LEFT, padx=2)

    def choose_color(self, fig, attr):
        color = colorchooser.askcolor()[1]
        if color:
            setattr(fig, attr, color)
            self.redraw()
            self.update_prop_panel()

    def set_prop(self, fig, attr, value):
        if attr in ('width', 'font_size'):
            try:
                value = int(value)
            except Exception:
                value = 12
        setattr(fig, attr, value)
        self.redraw()

    # --- Drag&Drop столбцов БД ---
    def start_drag_col(self, event, col):
        self.dragged_col = col
        # Визуализация "призрака" столбца
        if not self.drag_label:
            self.drag_label = tk.Label(self, text=col, bg="#ffe066", relief=tk.SOLID, bd=2)
        self.drag_label.place(x=event.x_root - self.winfo_rootx(), y=event.y_root - self.winfo_rooty())
        self.bind('<Motion>', self.drag_col_motion)
        self.bind('<ButtonRelease-1>', self.drop_col)
        self.canvas_drag_active = True

    def drag_col_motion(self, event):
        if self.drag_label:
            self.drag_label.place(x=event.x_root - self.winfo_rootx(), y=event.y_root - self.winfo_rooty())

    def drop_col(self, event):
        if self.dragged_col:
            # Координаты относительно Canvas
            x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            # Координаты должны быть внутри Canvas
            if 0 <= x <= self.canvas.winfo_width() and 0 <= y <= self.canvas.winfo_height():
                fig = Text(x, y, x+120, y+30, text=f'{{{self.dragged_col}}}', db_column=self.dragged_col, db_table=self.current_table)
                self.figures.append(fig)
                self.selected = fig
                self.redraw()
                self.update_prop_panel()
        if self.drag_label:
            self.drag_label.place_forget()
        self.dragged_col = None
        self.drag_label = None
        self.unbind('<Motion>')
        self.unbind('<ButtonRelease-1>')
        self.canvas_drag_active = False

    def on_drop_col(self, event):
        pass

    # --- Сохранение/загрузка шаблона ---
    def save_template(self):
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')])
        if not path:
            return
        data = []
        for fig in self.figures:
            d = fig.__dict__.copy()
            d['type'] = type(fig).__name__
            data.append(d)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo('Сохранено', f'Шаблон сохранён: {path}')

    def load_template(self):
        path = filedialog.askopenfilename(filetypes=[('JSON', '*.json')])
        if not path:
            return
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.figures.clear()
        for d in data:
            t = d.pop('type', 'Rectangle')
            d.pop('selected', None)  # Удаляем лишний ключ
            fig = None
            if t == 'Rectangle':
                keys = ('x1','y1','x2','y2','fill','outline','width')
                params = {k: d.get(k, Rectangle(0,0,0,0).fill if k=='fill' else Rectangle(0,0,0,0).outline if k=='outline' else 2 if k=='width' else 0) for k in keys}
                fig = Rectangle(**params)
            elif t == 'Ellipse':
                keys = ('x1','y1','x2','y2','fill','outline','width')
                params = {k: d.get(k, Ellipse(0,0,0,0).fill if k=='fill' else Ellipse(0,0,0,0).outline if k=='outline' else 2 if k=='width' else 0) for k in keys}
                fig = Ellipse(**params)
            elif t == 'Line':
                keys = ('x1','y1','x2','y2','outline','width')
                params = {k: d.get(k, Line(0,0,0,0).outline if k=='outline' else 2 if k=='width' else 0) for k in keys}
                fig = Line(**params)
            elif t == 'Text':
                # Поддержка старых и новых шаблонов
                params = {
                    'x1': d.get('x1', 0),
                    'y1': d.get('y1', 0),
                    'x2': d.get('x2', 0),
                    'y2': d.get('y2', 0),
                    'text': d.get('text', 'Текст'),
                    'fill': d.get('text_color', d.get('fill', '#000000')),
                    'font_size': d.get('font_size', 14),
                    'formula': d.get('formula', None),
                    'db_column': d.get('db_column', None),
                    'db_table': d.get('db_table', None),
                    'font_family': d.get('font_family', 'Segoe UI'),
                }
                fig = Text(**params)
            elif t == 'ButtonFigure':
                params = {
                    'x1': d.get('x1', 0),
                    'y1': d.get('y1', 0),
                    'x2': d.get('x2', 0),
                    'y2': d.get('y2', 0),
                    'text': d.get('text', 'Кнопка'),
                    'fill': d.get('fill', '#007bff'),
                    'outline': d.get('outline', '#0056b3'),
                    'width': d.get('width', 2),
                    'shape': d.get('shape', 'rect'),
                    'table': d.get('table', None),
                    'filters': d.get('filters', []),
                    'columns': d.get('columns', []),
                }
                fig = ButtonFigure(**params)
            if fig:
                self.figures.append(fig)
        self.selected = None
        self.redraw()
        self.update_prop_panel()

    def delete_selected(self):
        if self.selected and self.selected in self.figures:
            self.figures.remove(self.selected)
            self.selected = None
            self.redraw()
            self.update_prop_panel()

    def redraw(self):
        self.canvas.delete('all')
        for fig in self.figures:
            fig.selected = (fig == self.selected)
            fig.draw(self.canvas)

    def add_formula_field(self):
        formula = simpledialog.askstring("Формула", "Введите формулу (пример: {credit_limit} > 500000 and 'VIP' or ''):", parent=self)
        if not formula:
            return
        fig = Text(100, 100, 220, 130, text="{formula}", formula=formula)
        self.figures.append(fig)
        self.selected = fig
        self.redraw()
        self.update_prop_panel()

    def set_font_size(self, fig, spin):
        try:
            value = int(spin.get())
            fig.font_size = value
            self.redraw()
            self.update_prop_panel()
        except Exception:
            pass

    def add_filter(self, fig):
        if not fig.table:
            return
        # Все столбцы для фильтра
        col_names = [f'{fig.table}.{col["name"]}' for col in self.inspector.get_columns(fig.table)]
        fks = self.inspector.get_foreign_keys(fig.table)
        for fk in fks:
            ref_table = fk['referred_table']
            for col in self.inspector.get_columns(ref_table):
                col_names.append(f'{ref_table}.{col["name"]}')
        # Все поля карточки для подстановки
        card_fields = []
        for f in self.figures:
            if hasattr(f, 'db_column') and hasattr(f, 'db_table') and f.db_column and f.db_table:
                card_fields.append(f'{f.db_table}.{f.db_column}')
        win = tk.Toplevel(self)
        win.title("Добавить фильтр")
        tk.Label(win, text="Столбец:").pack()
        var_col = tk.StringVar(value=col_names[0])
        combo_col = ttk.Combobox(win, textvariable=var_col, values=col_names)
        combo_col.pack()
        tk.Label(win, text="Оператор:").pack()
        var_op = tk.StringVar(value='=')
        combo_op = ttk.Combobox(win, textvariable=var_op, values=['=', '!=', '>', '<', '>=', '<=', 'LIKE'])
        combo_op.pack()
        # Выбор типа значения
        var_type = tk.StringVar(value='manual')
        frame_type = tk.Frame(win)
        frame_type.pack(pady=2)
        tk.Radiobutton(frame_type, text="Ввести вручную", variable=var_type, value='manual').pack(side=tk.LEFT)
        tk.Radiobutton(frame_type, text="Подставить из карточки", variable=var_type, value='from_card').pack(side=tk.LEFT)
        # Значение вручную
        var_val = tk.StringVar()
        entry_val = tk.Entry(win, textvariable=var_val)
        entry_val.pack()
        # Значение из карточки
        var_field = tk.StringVar()
        combo_field = ttk.Combobox(win, textvariable=var_field, values=card_fields)
        def update_value_type(*a):
            if var_type.get() == 'manual':
                entry_val.pack()
                combo_field.pack_forget()
            else:
                entry_val.pack_forget()
                combo_field.pack()
        var_type.trace_add('write', update_value_type)
        update_value_type()
        def on_ok():
            if var_type.get() == 'manual':
                value = var_val.get()
            else:
                value = f'{{{var_field.get()}}}'
            f = {'column': var_col.get(), 'op': var_op.get(), 'value': value}
            if not hasattr(fig, 'filters') or fig.filters is None:
                fig.filters = []
            fig.filters.append(f)
            win.destroy()
            self.redraw()
            self.update_prop_panel()
        tk.Button(win, text="OK", command=on_ok).pack(pady=4)

    def del_filter(self, fig, idx):
        if hasattr(fig, 'filters') and fig.filters:
            fig.filters.pop(idx)
            self.redraw()
            self.update_prop_panel()

if __name__ == '__main__':
    CardEditor().mainloop() 