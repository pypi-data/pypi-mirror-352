"""
PGAdmin Site - библиотека для создания локального веб-интерфейса для работы с таблицами PostgreSQL.
"""

from .main import site, create_module_file
from .card_designer import CardEditor
from .zap import zap

def tkinter_card_designer(username=None, password=None, database=None, host='localhost', port=5432):
    CardEditor(username=username, password=password, database=database, host=host, port=port).mainloop()

__version__ = "0.2.0"
__all__ = ["site", "create_module_file", "tkinter_card_designer", "zap"] 