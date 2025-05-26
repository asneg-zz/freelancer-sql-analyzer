"""
Утилиты для построения промтов на основе анализа структуры таблиц
"""

from table_analyzer import TableAnalyzer


class PromptBuilder:
    """
    Класс для создания оптимизированных промтов на основе анализа данных
    """

    def __init__(self, db_path, table_name):
        self.analyzer = TableAnalyzer(db_path, table_name)
        self.is_analyzed = False

    def analyze_and_prepare(self):
        """Анализирует таблицу и подготавливает данные для промтов"""
        if self.analyzer.connect():
            self.analyzer.analyze_column_values()
            self.is_analyzed = True
            self.analyzer.disconnect()
            return True
        return False

    def build_enhanced_system_prompt(self):
        """Создает расширенный системный промт с анализом данных"""
        if not self.is_analyzed:
            return self.build_basic_system_prompt()

        base_prompt = self.build_basic_system_prompt()
        return self.analyzer.get_enhanced_system_prompt(base_prompt)

    def build_basic_system_prompt(self):
        """Создает базовый системный промт"""
        return """Создавай только SQL запросы для SQLite базы данных по запросу пользователя.
Отвечай только SQL запросом без дополнительных объяснений.

КРИТИЧЕСКИЕ ПРАВИЛА - ВСЕГДА СОБЛЮДАЙ:

1. АЛИАСЫ - используй ТОЧНЫЕ названия:
   - AS Average_Projects (НЕ Average_Jobs_Completed)
   - AS Average_Duration (НЕ Average_Job_Duration)
   - AS Average_Marketing (НЕ Average_Marketing_Spend)
   - AS Average_Rating (НЕ Average_Client_Rating)
   - AS Count (НЕ Number_of_Freelancers)
   - AS Percentage (НЕ Percentage_Fixed_Payment)

2. LIMIT - ВСЕГДА добавляй после GROUP BY:
   ✅ GROUP BY Platform ORDER BY Average_Rating DESC LIMIT 10
   ✅ GROUP BY Client_Region ORDER BY Max_Earnings DESC LIMIT 10
   ❌ GROUP BY Platform ORDER BY Average_Rating DESC (без LIMIT)
   Исключение: одиночные агрегаты без GROUP BY

3. ROUND - ОБЯЗАТЕЛЕН для ВСЕХ числовых агрегаций:
   ✅ ROUND(MAX(Client_Rating), 2) AS Max_Rating
   ❌ MAX(Client_Rating) AS Max_Rating

4. Payment_Method vs Project_Type:
   - Payment_Method = способы оплаты (Crypto, PayPal, Bank Transfer)
   - Project_Type = типы проектов (Fixed, Hourly)
   НЕ путай их!

5. SELECT * - используй когда нужны ВСЕ колонки:
   ✅ SELECT * FROM freelancer_earnings WHERE условие
   ❌ SELECT Freelancer_ID, Job_Success_Rate, Job_Completed FROM freelancer_earnings

6. СРАВНЕНИЕ ГРУПП - используй CASE WHEN, НЕ WITH:
   ✅ SELECT 
      ROUND(AVG(CASE WHEN Payment_Method = 'Crypto' THEN Earnings_USD END), 2) AS Crypto_Avg,
      ROUND(AVG(CASE WHEN Payment_Method != 'Crypto' THEN Earnings_USD END), 2) AS Other_Avg,
      ROUND(AVG(CASE WHEN Payment_Method = 'Crypto' THEN Earnings_USD END) - 
            AVG(CASE WHEN Payment_Method != 'Crypto' THEN Earnings_USD END), 2) AS Difference
      FROM freelancer_earnings
   ❌ WITH crypto_earners AS (...) - НЕ используй CTE для простых сравнений!

ШАБЛОНЫ ЗАПРОСОВ:

Топ-10 по заработку:
SELECT * FROM freelancer_earnings ORDER BY Earnings_USD DESC LIMIT 10

Количество в категориях:
SELECT Job_Category, COUNT(*) AS Count FROM freelancer_earnings 
GROUP BY Job_Category ORDER BY Count DESC LIMIT 10

Средний рейтинг по платформам:
SELECT Platform, ROUND(AVG(Client_Rating), 2) AS Average_Rating 
FROM freelancer_earnings GROUP BY Platform ORDER BY Average_Rating DESC LIMIT 10

Мин/макс по регионам:
SELECT Client_Region, ROUND(MIN(Earnings_USD), 2) AS Min_Earnings, 
ROUND(MAX(Earnings_USD), 2) AS Max_Earnings FROM freelancer_earnings 
GROUP BY Client_Region ORDER BY Max_Earnings DESC LIMIT 10

Средние проекты начинающих:
SELECT ROUND(AVG(Job_Completed), 2) AS Average_Projects 
FROM freelancer_earnings WHERE Experience_Level = 'Beginner'

Продолжительность по типам оплаты:
SELECT Payment_Method, ROUND(AVG(Job_Duration_Days), 2) AS Average_Duration 
FROM freelancer_earnings GROUP BY Payment_Method ORDER BY Average_Duration DESC LIMIT 10

Процент группы:
SELECT ROUND(COUNT(CASE WHEN Platform = 'Upwork' THEN 1 END) * 100.0 / COUNT(*), 2) AS Percentage 
FROM freelancer_earnings

Распределение по регионам:
SELECT Client_Region, ROUND(AVG(Earnings_USD), 2) AS Average_Earnings, 
COUNT(*) AS Count, ROUND(MIN(Earnings_USD), 2) AS Min_Earnings, 
ROUND(MAX(Earnings_USD), 2) AS Max_Earnings FROM freelancer_earnings 
GROUP BY Client_Region ORDER BY Average_Earnings DESC

ЗАПОМНИ:
- Не добавляй лишние слова к алиасам
- Всегда добавляй LIMIT 10 после GROUP BY
- Всегда используй ROUND(..., 2) для числовых агрегаций
- Используй простые CASE WHEN для сравнений, не WITH/CTE"""

    def get_table_summary(self):
        """Возвращает краткую сводку о таблице"""
        if not self.is_analyzed:
            return "Анализ не проведен"

        categorical = self.analyzer.get_categorical_columns()
        numeric = self.analyzer.get_numeric_columns()

        return f"""
СВОДКА ПО ТАБЛИЦЕ:
• Категориальных колонок: {len(categorical)}
• Числовых колонок: {len(numeric)}
• Основные категории: {', '.join(categorical[:3])}"""

    def get_improved_suggestions(self, user_input=""):
        """Генерирует предложения SQL запросов"""
        suggestions = []
        user_lower = user_input.lower()

        # Анализируем ключевые слова и создаем соответствующие запросы
        if "топ" in user_lower or "лучш" in user_lower:
            suggestions.append("SELECT * FROM freelancer_earnings ORDER BY Earnings_USD DESC LIMIT 10")

        if "средн" in user_lower:
            suggestions.append("SELECT ROUND(AVG(Earnings_USD), 2) AS Average_Earnings FROM freelancer_earnings")
            suggestions.append("SELECT Job_Category, ROUND(AVG(Earnings_USD), 2) AS Average_Earnings FROM freelancer_earnings GROUP BY Job_Category ORDER BY Average_Earnings DESC LIMIT 10")

        if "процент" in user_lower:
            suggestions.append("SELECT ROUND(COUNT(CASE WHEN Platform = 'Upwork' THEN 1 END) * 100.0 / COUNT(*), 2) AS Percentage FROM freelancer_earnings")
            suggestions.append("SELECT ROUND(COUNT(CASE WHEN Payment_Method = 'Crypto' THEN 1 END) * 100.0 / COUNT(*), 2) AS Percentage FROM freelancer_earnings")

        if "сравн" in user_lower or "выше" in user_lower:
            suggestions.append("""SELECT 
    ROUND(AVG(CASE WHEN Payment_Method = 'Crypto' THEN Earnings_USD END), 2) AS Crypto_Avg,
    ROUND(AVG(CASE WHEN Payment_Method != 'Crypto' THEN Earnings_USD END), 2) AS Other_Avg
FROM freelancer_earnings""")

        # Базовые предложения если нет специфических
        if not suggestions:
            suggestions = [
                "Покажи топ-10 фрилансеров по заработку",
                "Средний заработок по категориям работ",
                "Какой процент фрилансеров использует Upwork?",
                "Сравни доходы по способам оплаты"
            ]

        return suggestions[:5]

    def validate_and_suggest(self, user_input):
        """Валидирует запрос и предлагает оптимизированные SQL"""
        result = {
            'warnings': [],
            'suggestions': [],
            'validation_passed': True
        }

        user_lower = user_input.lower()

        # Проверка терминологии
        if "тип оплаты" in user_lower:
            result['warnings'].append("Используйте Payment_Method для способов оплаты")

        # Проверка на топ без сортировки
        if any(term in user_lower for term in ["топ", "лучш"]) and "order" not in user_lower:
            result['warnings'].append("Добавлена сортировка для топ-запроса")

        # Создаем оптимизированные запросы
        if "процент" in user_lower and "эксперт" in user_lower and "100 проект" in user_lower:
            result['suggestions'].append(
                "SELECT ROUND(COUNT(CASE WHEN Job_Completed < 100 THEN 1 END) * 100.0 / COUNT(*), 2) AS Percentage FROM freelancer_earnings WHERE Experience_Level = 'Expert'"
            )

        if "доход" in user_lower and "крипт" in user_lower and "сравн" in user_lower:
            result['suggestions'].append("""SELECT 
    ROUND(AVG(CASE WHEN Payment_Method = 'Crypto' THEN Earnings_USD END), 2) AS Crypto_Avg,
    ROUND(AVG(CASE WHEN Payment_Method != 'Crypto' THEN Earnings_USD END), 2) AS Other_Avg,
    ROUND(AVG(CASE WHEN Payment_Method = 'Crypto' THEN Earnings_USD END) - 
          AVG(CASE WHEN Payment_Method != 'Crypto' THEN Earnings_USD END), 2) AS Difference
FROM freelancer_earnings""")

        if "распредел" in user_lower and "доход" in user_lower and "регион" in user_lower:
            result['suggestions'].append(
                "SELECT Client_Region, ROUND(AVG(Earnings_USD), 2) AS Average_Earnings, COUNT(*) AS Count, ROUND(MIN(Earnings_USD), 2) AS Min_Earnings, ROUND(MAX(Earnings_USD), 2) AS Max_Earnings FROM freelancer_earnings GROUP BY Client_Region ORDER BY Average_Earnings DESC"
            )

        # Если нет специфических предложений, используем базовые
        if not result['suggestions']:
            result['suggestions'] = self.get_improved_suggestions(user_input)[:3]

        result['validation_passed'] = len(result['warnings']) == 0

        return result