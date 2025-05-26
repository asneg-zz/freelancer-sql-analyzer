"""
Общие утилиты для работы с SQL запросами
"""

import re
import sqlite3


def extract_sql_query(text):
    """
    Извлекает SQL запрос из текста ответа GigaChat
    """
    # Упрощенный подход - ищем SQL между маркерами или ключевые слова
    sql_match = re.search(r'```(?:sql)?\s*(.*?)\s*```', text, re.DOTALL | re.IGNORECASE)
    if sql_match:
        return sql_match.group(1).strip().rstrip(';')

    # Если не нашли в блоке кода, ищем SQL команды
    for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']:
        pattern = f'({keyword}.*?)(?:;|$)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip().rstrip(';')

    return None


def execute_sql_safely(conn, query):
    """
    Безопасно выполняет SQL запрос
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)

        if query.upper().strip().startswith('SELECT'):
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return True, results, columns
        else:
            conn.commit()
            return True, cursor.rowcount, []
    except Exception as e:
        return False, str(e), []


def normalize_sql(sql):
    """
    Нормализует SQL запрос для сравнения
    """
    if not sql:
        return ""

    # Убираем лишние пробелы и приводим к верхнему регистру ключевые слова
    normalized = re.sub(r'\s+', ' ', sql.strip().rstrip(';'))

    # Стандартизируем ключевые слова
    keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING',
                'LIMIT', 'AS', 'AND', 'OR', 'CASE', 'WHEN', 'THEN', 'END']

    for keyword in keywords:
        normalized = re.sub(f'\\b{keyword}\\b', keyword, normalized, flags=re.IGNORECASE)

    return normalized.strip()


def compare_sql_queries(generated_sql, expected_sql, table_name):
    """
    Сравнивает сгенерированный и ожидаемый SQL запросы
    """
    gen_norm = normalize_sql(generated_sql).lower()
    exp_norm = normalize_sql(expected_sql).lower()

    # Точное совпадение
    if gen_norm == exp_norm:
        return "exact_match", 100

    # Подсчет схожести по ключевым элементам
    elements = {
        'select': 15,
        f'from {table_name.lower()}': 15,
        'where': 10,
        'group by': 10,
        'order by': 10,
        'limit': 5,
        'count': 10,
        'avg': 10,
        'sum': 10,
        'round': 5
    }

    score = 0
    max_score = sum(elements.values())

    for element, weight in elements.items():
        if element in gen_norm and element in exp_norm:
            score += weight

    similarity_percent = min(100, (score / max_score) * 100)

    if similarity_percent >= 80:
        return "high_similarity", similarity_percent
    elif similarity_percent >= 60:
        return "medium_similarity", similarity_percent
    else:
        return "low_similarity", similarity_percent


def format_sql_results(success, results, columns, query, limit_rows=20):
    """
    Форматирует результаты выполнения SQL запроса
    """
    if not success:
        return f"❌ Ошибка выполнения SQL запроса: {results}"

    output = [f"\n📝 SQL запрос: {query}"]

    if query.upper().strip().startswith('SELECT'):
        if not results:
            output.append("Запрос выполнен, но результатов не найдено.")
        else:
            output.append("\nРезультат запроса:")
            output.append("-" * 50)

            # Заголовки
            if columns:
                header = " | ".join(columns)
                output.append(header)
                output.append("-" * len(header))

            # Данные
            for i, row in enumerate(results[:limit_rows]):
                output.append(" | ".join(str(item) for item in row))

            if len(results) > limit_rows:
                output.append(f"... и ещё {len(results) - limit_rows} строк")

            output.append(f"\nВсего записей: {len(results)}")
    else:
        output.append(f"Запрос выполнен успешно. Затронуто записей: {results}")

    return "\n".join(output)