"""
Модуль безопасности для проверки SQL запросов на предмет модифицирующих операций
"""

import re


class SQLSecurityValidator:
    """
    Класс для валидации безопасности SQL запросов
    """

    # Запрещенные SQL команды (DDL и DML операции изменения)
    FORBIDDEN_KEYWORDS = [
        # DDL операции
        'DROP', 'CREATE', 'ALTER', 'TRUNCATE', 'RENAME',
        # DML операции изменения
        'INSERT', 'UPDATE', 'DELETE', 'REPLACE', 'MERGE',
        # Административные операции
        'GRANT', 'REVOKE', 'COMMIT', 'ROLLBACK', 'SAVEPOINT',
        # Системные команды
        'PRAGMA', 'ATTACH', 'DETACH', 'VACUUM', 'REINDEX',
        # Опасные функции
        'EXEC', 'EXECUTE', 'CALL'
    ]

    # Разрешенные команды (только чтение)
    ALLOWED_KEYWORDS = [
        'SELECT', 'WITH', 'UNION', 'INTERSECT', 'EXCEPT'
    ]

    # Опасные функции и выражения
    DANGEROUS_PATTERNS = [
        r';\s*(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER)',  # Множественные команды
        r'--\s*',  # SQL комментарии (могут скрывать вредоносный код)
        r'/\*.*?\*/',  # Блочные комментарии
        r'UNION\s+ALL\s+SELECT.*FROM\s+sqlite_master',  # Попытка извлечь схему
        r'sqlite_master',  # Обращение к системным таблицам
        r'sqlite_sequence',
        r'sqlite_temp_master',
        r'LOAD_EXTENSION',  # Загрузка расширений
        r'randomblob\s*\(',  # Потенциально опасные функции
        r'hex\s*\(',
        r'char\s*\(',
    ]

    @classmethod
    def is_query_safe(cls, sql_query):
        """
        Проверяет безопасность SQL запроса

        Args:
            sql_query (str): SQL запрос для проверки

        Returns:
            tuple: (is_safe: bool, error_message: str or None)
        """
        if not sql_query or not isinstance(sql_query, str):
            return False, "Пустой или некорректный SQL запрос"

        # Нормализуем запрос
        normalized_query = sql_query.strip().upper()

        # Убираем лишние пробелы
        normalized_query = re.sub(r'\s+', ' ', normalized_query)

        # Проверка 1: Запрос должен начинаться с разрешенной команды
        first_word = normalized_query.split()[0] if normalized_query.split() else ""

        if first_word not in cls.ALLOWED_KEYWORDS:
            if first_word in cls.FORBIDDEN_KEYWORDS:
                return False, f"Запрещена модифицирующая операция: {first_word}"
            else:
                return False, f"Неразрешенная SQL команда: {first_word}"

        # Проверка 2: Поиск запрещенных ключевых слов в запросе
        for keyword in cls.FORBIDDEN_KEYWORDS:
            # Ищем ключевое слово как отдельное слово (с границами)
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, normalized_query):
                return False, f"Обнаружена запрещенная операция: {keyword}"

        # Проверка 3: Поиск опасных паттернов
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, normalized_query, re.IGNORECASE | re.DOTALL):
                return False, f"Обнаружен потенциально опасный паттерн в запросе"

        # Проверка 4: Множественные команды (через точку с запятой)
        statements = [stmt.strip() for stmt in sql_query.split(';') if stmt.strip()]
        if len(statements) > 1:
            return False, "Множественные SQL команды запрещены"

        # Проверка 5: Проверка на SQL инъекции
        injection_patterns = [
            r"'\s*;\s*",  # Закрытие кавычки с последующей командой
            r'"\s*;\s*',  # То же с двойными кавычками
            r"'\s*(OR|AND)\s*'",  # Простые булевы инъекции
            r'"\s*(OR|AND)\s*"',
            r"'\s*OR\s+1\s*=\s*1",  # Классические инъекции
            r"'\s*OR\s+TRUE",
            r"1\s*=\s*1\s*--",
        ]

        for pattern in injection_patterns:
            if re.search(pattern, sql_query, re.IGNORECASE):
                return False, "Обнаружена попытка SQL инъекции"

        return True, None

    @classmethod
    def validate_and_clean_query(cls, sql_query):
        """
        Валидирует и очищает SQL запрос

        Args:
            sql_query (str): Исходный SQL запрос

        Returns:
            tuple: (cleaned_query: str or None, error_message: str or None)
        """
        is_safe, error_msg = cls.is_query_safe(sql_query)

        if not is_safe:
            return None, error_msg

        # Очищаем запрос от потенциально опасных элементов
        cleaned_query = sql_query.strip()

        # Убираем комментарии
        cleaned_query = re.sub(r'--.*$', '', cleaned_query, flags=re.MULTILINE)
        cleaned_query = re.sub(r'/\*.*?\*/', '', cleaned_query, flags=re.DOTALL)

        # Убираем лишние пробелы
        cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()

        # Убираем точку с запятой в конце
        cleaned_query = cleaned_query.rstrip(';')

        return cleaned_query, None

    @classmethod
    def get_security_info(cls):
        """
        Возвращает информацию о правилах безопасности

        Returns:
            str: Описание правил безопасности
        """
        return f"""
🔒 ПРАВИЛА БЕЗОПАСНОСТИ SQL:

✅ РАЗРЕШЕННЫЕ ОПЕРАЦИИ:
- SELECT (выборка данных)
- WITH (временные таблицы для сложных запросов)
- UNION, INTERSECT, EXCEPT (объединение результатов)

❌ ЗАПРЕЩЕННЫЕ ОПЕРАЦИИ:
- Модификация данных: INSERT, UPDATE, DELETE, REPLACE
- Изменение структуры: CREATE, DROP, ALTER, TRUNCATE
- Административные: GRANT, REVOKE, PRAGMA
- Системные функции и таблицы

🛡️ ДОПОЛНИТЕЛЬНЫЕ ОГРАНИЧЕНИЯ:
- Запрещены множественные команды (через ;)
- Блокируются SQL комментарии
- Предотвращаются попытки SQL инъекций
- Запрещен доступ к системным таблицам SQLite

Система работает только в режиме ЧТЕНИЯ данных!
        """


def test_security_validator():
    """
    Тестирование валидатора безопасности
    """
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ БЕЗОПАСНОСТИ SQL")
    print("=" * 50)

    # Безопасные запросы
    safe_queries = [
        "SELECT * FROM freelancer_earnings LIMIT 10",
        "SELECT COUNT(*) FROM freelancer_earnings WHERE Experience_Level = 'Expert'",
        "SELECT Platform, AVG(Earnings_USD) FROM freelancer_earnings GROUP BY Platform",
        "WITH top_earners AS (SELECT * FROM freelancer_earnings ORDER BY Earnings_USD DESC LIMIT 10) SELECT * FROM top_earners"
    ]

    # Опасные запросы
    dangerous_queries = [
        "DROP TABLE freelancer_earnings",
        "DELETE FROM freelancer_earnings WHERE id = 1",
        "INSERT INTO freelancer_earnings VALUES (1, 'test')",
        "UPDATE freelancer_earnings SET Earnings_USD = 0",
        "SELECT * FROM freelancer_earnings; DROP TABLE freelancer_earnings;",
        "SELECT * FROM sqlite_master",
        "SELECT * FROM freelancer_earnings WHERE name = 'test'; --",
        "SELECT * FROM freelancer_earnings WHERE id = 1 OR 1=1",
        "CREATE TABLE test (id INT)",
        "ALTER TABLE freelancer_earnings ADD COLUMN test VARCHAR(100)",
        "PRAGMA table_info(freelancer_earnings)"
    ]

    print("✅ ТЕСТИРОВАНИЕ БЕЗОПАСНЫХ ЗАПРОСОВ:")
    for i, query in enumerate(safe_queries, 1):
        is_safe, error = SQLSecurityValidator.is_query_safe(query)
        status = "✅ БЕЗОПАСЕН" if is_safe else f"❌ ОПАСЕН: {error}"
        print(f"{i}. {status}")
        print(f"   Запрос: {query[:50]}...")

    print(f"\n❌ ТЕСТИРОВАНИЕ ОПАСНЫХ ЗАПРОСОВ:")
    for i, query in enumerate(dangerous_queries, 1):
        is_safe, error = SQLSecurityValidator.is_query_safe(query)
        status = "✅ ЗАБЛОКИРОВАН" if not is_safe else "❌ ПРОПУЩЕН (ОШИБКА!)"
        print(f"{i}. {status}")
        if not is_safe:
            print(f"   Причина: {error}")
        print(f"   Запрос: {query[:50]}...")


if __name__ == "__main__":
    test_security_validator()