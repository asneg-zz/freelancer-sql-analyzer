# Тестовые вопросы и правильные SQL запросы для freelancer_earnings

TEST_CASES = [
    {
        "id": 1,
        "question": "Покажи топ-10 фрилансеров по заработку",
        "expected_sql": "SELECT * FROM freelancer_earnings ORDER BY Earnings_USD DESC LIMIT 10",
        "category": "basic_sorting"
    },
    {
        "id": 2,
        "question": "Какой средний заработок у экспертов?",
        "expected_sql": "SELECT ROUND(AVG(Earnings_USD), 2) AS Average_Earnings FROM freelancer_earnings WHERE Experience_Level = 'Expert'",
        "category": "aggregation"
    },
    {
        "id": 3,
        "question": "Сколько фрилансеров работает в каждой категории?",
        "expected_sql": "SELECT Job_Category, COUNT(*) AS Count FROM freelancer_earnings GROUP BY Job_Category ORDER BY Count DESC LIMIT 10",
        "category": "grouping"
    },
    {
        "id": 4,
        "question": "Какой процент фрилансеров использует Upwork?",
        "expected_sql": "SELECT ROUND(COUNT(CASE WHEN Platform = 'Upwork' THEN 1 END) * 100.0 / COUNT(*), 2) AS Percentage FROM freelancer_earnings",
        "category": "percentage"
    },
    {
        "id": 5,
        "question": "Средний рейтинг клиентов по каждой платформе",
        "expected_sql": "SELECT Platform, ROUND(AVG(Client_Rating), 2) AS Average_Rating FROM freelancer_earnings GROUP BY Platform ORDER BY Average_Rating DESC LIMIT 10",
        "category": "grouping"
    },
    {
        "id": 6,
        "question": "Фрилансеры с почасовой ставкой выше 50 долларов",
        "expected_sql": "SELECT * FROM freelancer_earnings WHERE Hourly_Rate > 50 ORDER BY Hourly_Rate DESC LIMIT 10",
        "category": "filtering"
    },
    {
        "id": 7,
        "question": "Какой минимальный и максимальный заработок в каждом регионе?",
        "expected_sql": "SELECT Client_Region, ROUND(MIN(Earnings_USD), 2) AS Min_Earnings, ROUND(MAX(Earnings_USD), 2) AS Max_Earnings FROM freelancer_earnings GROUP BY Client_Region ORDER BY Max_Earnings DESC LIMIT 10",
        "category": "aggregation"
    },
    {
        "id": 8,
        "question": "Сколько проектов в среднем выполняют начинающие фрилансеры?",
        "expected_sql": "SELECT ROUND(AVG(Job_Completed), 2) AS Average_Projects FROM freelancer_earnings WHERE Experience_Level = 'Beginner'",
        "category": "aggregation"
    },
    {
        "id": 9,
        "question": "Фрилансеры из категории Web Development с рейтингом выше 4.5",
        "expected_sql": "SELECT * FROM freelancer_earnings WHERE Job_Category = 'Web Development' AND Client_Rating > 4.5 ORDER BY Client_Rating DESC LIMIT 10",
        "category": "filtering"
    },
    {
        "id": 10,
        "question": "Средняя продолжительность проекта по типам оплаты",
        "expected_sql": "SELECT Payment_Method, ROUND(AVG(Job_Duration_Days), 2) AS Average_Duration FROM freelancer_earnings GROUP BY Payment_Method ORDER BY Average_Duration DESC LIMIT 10",
        "category": "grouping"
    },
    {
        "id": 11,
        "question": "Какой процент проектов имеет фиксированную оплату?",
        "expected_sql": "SELECT ROUND(COUNT(CASE WHEN Project_Type = 'Fixed' THEN 1 END) * 100.0 / COUNT(*), 2) AS Percentage FROM freelancer_earnings",
        "category": "percentage"
    },
    {
        "id": 12,
        "question": "Топ-5 платформ по среднему заработку",
        "expected_sql": "SELECT Platform, ROUND(AVG(Earnings_USD), 2) AS Average_Earnings FROM freelancer_earnings GROUP BY Platform ORDER BY Average_Earnings DESC LIMIT 5",
        "category": "grouping"
    },
    {
        "id": 13,
        "question": "Фрилансеры с процентом успеха выше 90% и более 100 проектов",
        "expected_sql": "SELECT * FROM freelancer_earnings WHERE Job_Success_Rate > 90 AND Job_Completed > 100 ORDER BY Job_Success_Rate DESC LIMIT 10",
        "category": "filtering"
    },
    {
        "id": 14,
        "question": "Средние расходы на маркетинг по уровням опыта",
        "expected_sql": "SELECT Experience_Level, ROUND(AVG(Marketing_Spend), 2) AS Average_Marketing FROM freelancer_earnings GROUP BY Experience_Level ORDER BY Average_Marketing DESC LIMIT 10",
        "category": "grouping"
    },
    {
        "id": 15,
        "question": "Сколько фрилансеров получают оплату криптовалютой?",
        "expected_sql": "SELECT COUNT(*) AS Crypto_Freelancers FROM freelancer_earnings WHERE Payment_Method = 'Crypto'",
        "category": "counting"
    },
    {
        "id": 16,
        "question": "Фрилансеры из Азии с заработком более 7000 долларов",
        "expected_sql": "SELECT * FROM freelancer_earnings WHERE Client_Region = 'Asia' AND Earnings_USD > 7000 ORDER BY Earnings_USD DESC LIMIT 10",
        "category": "filtering"
    },
    {
        "id": 17,
        "question": "Средний процент повторного найма по категориям работ",
        "expected_sql": "SELECT Job_Category, ROUND(AVG(Rehire_Rate), 2) AS Average_Rehire_Rate FROM freelancer_earnings GROUP BY Job_Category ORDER BY Average_Rehire_Rate DESC LIMIT 10",
        "category": "grouping"
    },
    {
        "id": 18,
        "question": "Какой процент экспертов выполнил менее 100 проектов?",
        "expected_sql": "SELECT ROUND(COUNT(CASE WHEN Job_Completed < 100 THEN 1 END) * 100.0 / COUNT(*), 2) AS Percentage FROM freelancer_earnings WHERE Experience_Level = 'Expert'",
        "category": "percentage"
    },
    {
        "id": 19,
        "question": "Фрилансеры с самым высоким рейтингом клиентов в каждой категории",
        "expected_sql": "SELECT Job_Category, ROUND(MAX(Client_Rating), 2) AS Max_Rating FROM freelancer_earnings GROUP BY Job_Category ORDER BY Max_Rating DESC LIMIT 10",
        "category": "grouping"
    },
    {
        "id": 20,
        "question": "Средняя почасовая ставка для проектов продолжительностью более 30 дней",
        "expected_sql": "SELECT ROUND(AVG(Hourly_Rate), 2) AS Average_Hourly_Rate FROM freelancer_earnings WHERE Job_Duration_Days > 30",
        "category": "aggregation"
    },
    {
        "id": 21,
        "question": "Насколько выше доход у фрилансеров, принимающих оплату в криптовалюте, по сравнению с другими способами оплаты?",
        "expected_sql": "SELECT ROUND(AVG(CASE WHEN Payment_Method = 'Crypto' THEN Earnings_USD END), 2) AS Crypto_Avg, ROUND(AVG(CASE WHEN Payment_Method != 'Crypto' THEN Earnings_USD END), 2) AS Other_Avg, ROUND(AVG(CASE WHEN Payment_Method = 'Crypto' THEN Earnings_USD END) - AVG(CASE WHEN Payment_Method != 'Crypto' THEN Earnings_USD END), 2) AS Difference FROM freelancer_earnings",
        "category": "comparison"
    },
    {
        "id": 22,
        "question": "Как распределяется доход фрилансеров в зависимости от региона проживания?",
        "expected_sql": "SELECT Client_Region, ROUND(AVG(Earnings_USD), 2) AS Average_Earnings, COUNT(*) AS Count, ROUND(MIN(Earnings_USD), 2) AS Min_Earnings, ROUND(MAX(Earnings_USD), 2) AS Max_Earnings FROM freelancer_earnings GROUP BY Client_Region ORDER BY Average_Earnings DESC",
        "category": "distribution"
    },
    {
        "id": 23,
        "question": "Какой процент фрилансеров, считающих себя экспертами, выполнил менее 100 проектов?",
        "expected_sql": "SELECT ROUND(COUNT(CASE WHEN Job_Completed < 100 THEN 1 END) * 100.0 / COUNT(*), 2) AS Percentage FROM freelancer_earnings WHERE Experience_Level = 'Expert'",
        "category": "percentage"
    }
]

# Категории тестов для анализа
TEST_CATEGORIES = {
    "basic_sorting": "Базовая сортировка",
    "aggregation": "Агрегация данных",
    "grouping": "Группировка",
    "percentage": "Процентные расчеты",
    "filtering": "Фильтрация",
    "counting": "Подсчет записей",
    "comparison": "Сравнение групп",
    "distribution": "Распределение данных"
}