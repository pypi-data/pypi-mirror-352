import json
import os
from typing import Any, Dict


class GramLib:
    def __init__(self, filename: str):
        if not filename.endswith(".gram"):
            raise ValueError("Имя файла должно иметь расширение '.gram'")
        self.filename = filename
        self.data: Dict[str, Any] = {}
        self.is_open: bool = False

    def create_table(self, overwrite: bool = False, **kwargs) -> "GramLib":
        if os.path.exists(self.filename):
            if not overwrite:
                raise FileExistsError(
                    f"Таблица '{self.filename}' уже существует. "
                    "Используйте open_table для работы с ней или передайте overwrite=True для перезаписи."
                )
        self.data = kwargs
        self.save_data()
        self.is_open = True
        return self

    def open_table(self) -> "GramLib":
        if self.is_open:
            raise RuntimeError("Таблица уже открыта.")
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"Таблица '{self.filename}' не найдена.")
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Файл '{self.filename}' повреждён или не является корректным JSON.")
        self.is_open = True
        return self

    def save_data(self) -> None:
        if not self.is_open:
            raise RuntimeError("Таблица не открыта. Откройте таблицу перед сохранением.")
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def close(self) -> "GramLib":
        if not self.is_open:
            raise RuntimeError("Таблица не открыта, закрывать нечего.")
        self.save_data()
        self.is_open = False
        return self

    def delete_table(self) -> None:
        if os.path.exists(self.filename):
            os.remove(self.filename)
        else:
            raise FileNotFoundError(f"Таблица '{self.filename}' не существует.")

    def create_key(self, key: str, value: Any) -> "GramLib":
        self._ensure_open()
        self.data[key] = value
        return self

    def delete_key(self, key: str) -> "GramLib":
        self._ensure_open()
        if key not in self.data:
            raise KeyError(f"Ключ '{key}' не найден в таблице.")
        del self.data[key]
        return self

    def update(self, key: str, value: Any) -> str:
        self._ensure_open()
        updated_count = 0
        for record_key, record_value in self.data.items():
            if isinstance(record_value, dict):
                record_value[key] = value
                updated_count += 1
        self.save_data()
        return f"Обновлено {updated_count} записей с ключом '{key}'."

    def run(self, **kwargs) -> str:
        if not kwargs:
            return f"Запуск базы данных: {self.filename}"
        for db_file, flag in kwargs.items():
            if not (isinstance(db_file, str) and db_file.endswith(".gram") and flag is True):
                raise ValueError(
                    "Неверный формат аргументов для run(). "
                    "Используйте gramlib.run(имя_файла.gram=True)"
                )
            return f"Запуск базы данных: {db_file}"

    def help(self) -> None:
        help_text = """
Доступные методы GramLib:

  create_table(**kwargs, overwrite=False) - Создать новую таблицу. Если файл существует, можно перезаписать.
  open_table()                           - Открыть существующую таблицу.
  save_data()                           - Сохранить текущие данные в файл.
  close()                              - Сохранить и закрыть таблицу.
  create_key(key, value)                - Добавить или обновить ключ в таблице.
  delete_key(key)                      - Удалить ключ из таблицы.
  delete_table()                      - Удалить файл таблицы.
  update(key, value)                   - Пакетно обновить ключ во всех записях.
  run(**kwargs)                        - Запустить базу с параметрами.
  help()                              - Показать это сообщение.

Пример использования:
  gram = GramLib("test.gram")
  gram.create_table(user1={"name": "Иван"})
  gram.open_table()
  gram.create_key("city", "Moscow")
  print(gram.update("age", 30))
  gram.close()
"""
        print(help_text)

    def _ensure_open(self) -> None:
        if not self.is_open:
            raise RuntimeError("Таблица не открыта. Сначала вызовите open_table() или create_table().")
