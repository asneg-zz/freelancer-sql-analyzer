import sqlite3
from collections import Counter
import statistics


class TableAnalyzer:
    """
    Класс для анализа таблиц в базе данных SQLite.
    """

    def __init__(self, db_path, table_name):
        self.db_path = db_path
        self.table_name = table_name
        self.connection = None
        self.column_info = {}

    def connect(self):
        """Устанавливает соединение с базой данных"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False

    def disconnect(self):
        """Закрывает соединение с базой данных"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def analyze_column_values(self, limit_per_column=50):
        """
        Анализирует уникальные значения в каждой колонке
        """
        if not self.connection:
            return

        try:
            cursor = self.connection.cursor()

            # Получаем информацию о колонках
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            table_info = cursor.fetchall()

            for col_info in table_info:
                column_name = col_info[1]
                column_type = col_info[2]

                # Получаем все значения из колонки
                cursor.execute(f"SELECT {column_name} FROM {self.table_name} WHERE {column_name} IS NOT NULL")
                values = [row[0] for row in cursor.fetchall()]

                if not values:
                    continue

                # Определяем тип данных
                is_numeric = self._is_numeric_column(values)

                # Подсчитываем уникальные значения
                unique_values = list(set(values))
                value_counts = Counter(values)

                self.column_info[column_name] = {
                    'type': column_type,
                    'is_numeric': is_numeric,
                    'total_count': len(values),
                    'unique_count': len(unique_values),
                    'unique_values': [],
                    'range': None
                }

                if is_numeric:
                    # Для числовых колонок сохраняем диапазон
                    numeric_values = [float(v) for v in values]
                    self.column_info[column_name]['range'] = {
                        'min': min(numeric_values),
                        'max': max(numeric_values),
                        'mean': statistics.mean(numeric_values)
                    }
                    # Сохраняем уникальные значения только если их немного
                    if len(unique_values) <= 20:
                        self.column_info[column_name]['unique_values'] = sorted(unique_values)
                else:
                    # Для текстовых колонок сохраняем уникальные значения
                    if len(unique_values) <= limit_per_column:
                        self.column_info[column_name]['unique_values'] = sorted(unique_values)
                    else:
                        # Если много значений, берем самые частые
                        top_values = value_counts.most_common(limit_per_column)
                        self.column_info[column_name]['unique_values'] = [v for v, _ in top_values]

        except sqlite3.Error as e:
            print(f"Ошибка анализа колонок: {e}")

    def _is_numeric_column(self, values):
        """Определяет, является ли колонка числовой"""
        if not values:
            return False

        # Проверяем первые 100 значений
        sample = values[:100]
        numeric_count = sum(1 for v in sample if self._is_numeric(v))

        return numeric_count / len(sample) > 0.9

    def _is_numeric(self, value):
        """Проверяет, является ли значение числом"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    def get_categorical_columns(self):
        """Возвращает список категориальных колонок"""
        return [col for col, info in self.column_info.items()
                if not info['is_numeric'] or info['unique_count'] <= 50]

    def get_numeric_columns(self):
        """Возвращает список числовых колонок"""
        return [col for col, info in self.column_info.items()
                if info['is_numeric']]

    def generate_prompt_schema(self):
        """Генерирует схему таблицы для промта"""
        if not self.column_info:
            return "Анализ таблицы не проведён"

        result = [f"ТАБЛИЦА: {self.table_name}\n"]

        # Категориальные колонки
        categorical = self.get_categorical_columns()
        if categorical:
            result.append("КАТЕГОРИАЛЬНЫЕ КОЛОНКИ:")
            for col in categorical:
                info = self.column_info[col]
                if info['unique_values']:
                    values_str = ", ".join(str(v) for v in info['unique_values'][:30])
                    result.append(f"- {col}: {values_str}")
                else:
                    result.append(f"- {col}: {info['unique_count']} уникальных значений")

        # Числовые колонки
        numeric = self.get_numeric_columns()
        if numeric:
            result.append("\nЧИСЛОВЫЕ КОЛОНКИ:")
            for col in numeric:
                info = self.column_info[col]
                if info['range']:
                    r = info['range']
                    result.append(f"- {col}: от {r['min']:.2f} до {r['max']:.2f}")

        return "\n".join(result)

    def generate_system_prompt_addition(self):
        """Генерирует дополнение к системному промту"""
        categorical = self.get_categorical_columns()

        if not categorical:
            return ""

        result = ["\nВОЗМОЖНЫЕ ЗНАЧЕНИЯ В КОЛОНКАХ:"]

        for col in categorical:
            info = self.column_info[col]
            if info['unique_values'] and len(info['unique_values']) <= 20:
                values_str = ", ".join(str(v) for v in info['unique_values'])
                result.append(f"{col}: {values_str}")

        result.extend([
            "\nОБЯЗАТЕЛЬНО используй только эти точные значения при формировании WHERE условий.",
            "Используй SQLite синтаксис и ROUND() для округления числовых результатов."
        ])

        return "\n".join(result)

    def get_enhanced_system_prompt(self, base_prompt):
        """Создает расширенный системный промт"""
        schema_info = self.generate_prompt_schema()
        values_info = self.generate_system_prompt_addition()
        return f"{base_prompt}\n\n{schema_info}\n{values_info}"