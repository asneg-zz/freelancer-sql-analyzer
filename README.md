# 🤖 SQL Generator с GigaChat

Система для автоматической генерации SQL запросов на основе вопросов на естественном языке с использованием GigaChat API.


## 🚀 Возможности

- ✅ **Генерация SQL из естественного языка** - задавайте вопросы обычными словами
- ✅ **Автоматический анализ данных** - система сама изучает структуру ваших данных
- ✅ **Безопасность** - выполняются только SELECT запросы, защита от SQL инъекций
- ✅ **Интерактивный интерфейс** - удобная работа через консоль
- ✅ **Поддержка CSV** - загружайте любые табличные данные
- ✅ **Умные промпты** - система знает особенности ваших данных

## 📋 Требования

- Python 3.8 или выше
- Учетная запись GigaChat API ([получить здесь](https://developers.sber.ru/gigachat))
- Отчет о входных данных ([получить здесь](https://github.com/asneg-zz/freelancer-sql-analyzer/blob/main/Text-to-sql_1.ipynb))

## 🛠 Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/asneg-zz/sql-generator.git
cd sql-generator
```

### 2. Создание виртуального окружения (рекомендуется)
```bash
python -m venv venv

# Активация
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка GigaChat API

#### Получение учетных данных:
1. Перейдите на https://developers.sber.ru/gigachat
2. Зарегистрируйтесь и создайте приложение
3. Получите учетные данные (credentials)

#### Настройка credentials:

**Вариант 1 - Переменная окружения (рекомендуется):**
```bash
# Windows
set GIGACHAT_CREDENTIALS=ваши_учетные_данные

# Linux/Mac
export GIGACHAT_CREDENTIALS="ваши_учетные_данные"
```

**Вариант 2 - Файл .env:**
```bash
echo "GIGACHAT_CREDENTIALS=ваши_учетные_данные" > .env
```

## 🎯 Быстрый старт

```bash
python main.py
```

Система автоматически:
1. 📊 Загрузит демонстрационные данные (`freelancer_earnings_bd.csv`)
2. 🗄️ Создаст SQLite базу данных
3. 🔍 Проанализирует структуру данных
4. 🚀 Запустит интерактивный режим

## 💬 Примеры использования

### Простые запросы:
```
💬 Ваш вопрос: Покажи топ-10 фрилансеров по заработку
🤖 Генерирую SQL запрос...
📝 SQL: SELECT * FROM freelancer_earnings ORDER BY Earnings_USD DESC LIMIT 10

💬 Ваш вопрос: Сколько фрилансеров в каждой категории?
🤖 Генерирую SQL запрос...
📝 SQL: SELECT Job_Category, COUNT(*) AS Count 
        FROM freelancer_earnings GROUP BY Job_Category 
        ORDER BY Count DESC LIMIT 10
```

### Аналитические запросы:
```
💬 Ваш вопрос: Средний заработок по регионам
🤖 Генерирую SQL запрос...
📝 SQL: SELECT Client_Region, ROUND(AVG(Earnings_USD), 2) AS Average_Earnings 
        FROM freelancer_earnings GROUP BY Client_Region 
        ORDER BY Average_Earnings DESC

💬 Ваш вопрос: Какой процент фрилансеров использует криптовалюту?
🤖 Генерирую SQL запрос...
📝 SQL: SELECT ROUND(COUNT(CASE WHEN Payment_Method = 'Crypto' THEN 1 END) * 100.0 / COUNT(*), 2) AS Percentage 
        FROM freelancer_earnings
```

### Сложные запросы:
```
💬 Ваш вопрос: Сравни доходы фрилансеров с криптооплатой и без неё
🤖 Генерирую SQL запрос...
📝 SQL: SELECT 
    ROUND(AVG(CASE WHEN Payment_Method = 'Crypto' THEN Earnings_USD END), 2) AS Crypto_Avg,
    ROUND(AVG(CASE WHEN Payment_Method != 'Crypto' THEN Earnings_USD END), 2) AS Other_Avg
FROM freelancer_earnings
```

## 📊 Работа с собственными данными

### 1. Подготовка CSV файла
Убедитесь, что ваш CSV файл имеет:
- Заголовки в первой строке
- Корректную кодировку (UTF-8)
- Разделитель - запятая

### 2. Запуск с вашими данными
```python
from main import SQLGenerator

# Создание генератора с вашим файлом
generator = SQLGenerator('your_data.csv', 'your_database.db')

if generator.setup():
    generator.run_interactive()
```

### 3. Программное использование
```python
# Генерация SQL
sql = generator.generate_sql("Покажи топ-10 записей")
print(f"SQL: {sql}")

# Выполнение запроса
results, error = generator.execute_query(sql)
if results:
    print("Результаты:", results)
else:
    print("Ошибка:", error)
```

## 🗂 Структура проекта

```
sql-generator/
├── 📄 main.py                 # Основной файл приложения
├── ⚙️ config.py               # Конфигурация GigaChat
├── 📊 sql_analyzer.py         # Анализ структуры данных
├── 🛠️ utils.py                # Вспомогательные функции
├── 📋 prompt_builder.py       # Построение промптов
├── 🔍 table_analyzer.py       # Анализ таблиц
├── 🔒 sql_security.py         # Безопасность SQL
├── 📦 requirements.txt        # Зависимости Python
├── 📖 README.md              # Документация
├── 📈 freelancer_earnings_bd.csv # Демо данные
└── 🧪 examples/              # Примеры использования
    ├── basic_usage.py
    └── advanced_usage.py
```

## 🔧 Команды интерфейса

В интерактивном режиме доступны команды:

| Команда | Описание |
|---------|----------|
| `help` | Показать справку по использованию |
| `schema` | Показать структуру загруженных данных |
| `examples` | Показать примеры запросов |
| `suggest <текст>` | Получить умные предложения запросов |
| `validate <текст>` | Проверить корректность запроса |
| `exit` | Выход из программы |

## 🛡 Безопасность

Система включает несколько уровней защиты:

- ✅ **Только SELECT запросы** - блокируются INSERT, UPDATE, DELETE
- ✅ **Защита от SQL инъекций** - валидация входных данных
- ✅ **Блокировка системных команд** - нет доступа к DROP, CREATE и др.
- ✅ **Учетные данные в переменных окружения** - не хранятся в коде
- ✅ **Тайм-ауты запросов** - защита от зависания

## 🔧 API для разработчиков

### Базовое использование:
```python
from main import SQLGenerator

# Инициализация
generator = SQLGenerator('data.csv')
generator.setup()

# Генерация SQL
sql = generator.generate_sql("Найди записи с высоким рейтингом")
print(f"Сгенерированный SQL: {sql}")

# Выполнение
results, error = generator.execute_query(sql)
```

### Продвинутое использование:
```python
from sql_analyzer import SQLAnalyzer
from prompt_builder import PromptBuilder

# Анализ данных
analyzer = SQLAnalyzer('database.db', 'table_name')
analyzer.analyze_and_prepare()

# Построение промптов
builder = PromptBuilder('database.db', 'table_name')
system_prompt = builder.build_enhanced_system_prompt()
```

## ⚡ Производительность

- **Время генерации SQL:** 1-3 секунды
- **Поддерживаемый размер данных:** до 1 млн записей
- **Максимальное время выполнения запроса:** 30 секунд
- **Кэширование:** Включено для промптов и результатов

## 🧪 Тестирование

### Запуск базовых тестов:
```bash
python -m pytest tests/ -v
```

### Тестирование с вашими данными:
```bash
python main_test.py
```

## 🔧 Устранение неполадок

### Частые проблемы:

**❌ Ошибка подключения к GigaChat:**
```
Решение: Проверьте GIGACHAT_CREDENTIALS в переменных окружения
```

**❌ Файл CSV не найден:**
```
Решение: Убедитесь, что файл существует и путь указан корректно
```

**❌ Ошибка SQL запроса:**
```
Решение: Проверьте названия колонок командой 'schema'
```

**❌ Медленная работа:**
```
Решение: Уменьшите размер данных или добавьте индексы
```

### Отладка:
```python
# Включение подробных логов
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! 

### Как внести вклад:
1. 🍴 Форкните репозиторий
2. 🌿 Создайте ветку для новой функции: `git checkout -b feature/новая-функция`
3. ✨ Внесите изменения и добавьте тесты
4. 📝 Обновите документацию при необходимости
5. 🚀 Создайте Pull Request

### Правила разработки:
- Следуйте PEP 8 для стиля кода
- Добавляйте тесты для новых функций
- Обновляйте README при добавлении функционала

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

## 🙋‍♂️ Поддержка

### Где получить помощь:

- 📧 **Email:** support@example.com
- 🐛 **Баги:** [GitHub Issues](https://github.com/asneg-zz/sql-generator/issues)
- 💬 **Обсуждения:** [GitHub Discussions](https://github.com/asneg-zz/sql-generator/discussions)
- 📖 **Документация:** [Wiki](https://github.com/asneg-zz/sql-generator/wiki)

### Часто задаваемые вопросы:

**Q: Поддерживаются ли другие LLM кроме GigaChat?**
A: В текущей версии только GigaChat, но архитектура позволяет легко добавить другие модели.

**Q: Можно ли использовать с PostgreSQL/MySQL?**
A: Сейчас только SQLite, но планируется поддержка других СУБД.

**Q: Есть ли ограничения на размер данных?**
A: Рекомендуется до 1 млн записей для оптимальной производительности.

## 🚀 Дорожная карта

### Планируемые функции:

- [ ] Поддержка PostgreSQL и MySQL
- [ ] Веб-интерфейс
- [ ] Экспорт результатов в Excel/CSV
- [ ] Визуализация данных
- [ ] Поддержка других LLM (OpenAI, Claude)
- [ ] Кэширование запросов
- [ ] Batch обработка

### Версии:

- **v1.0.0** - Базовая функциональность ✅
- **v1.1.0** - Улучшенный анализ данных (планируется)
- **v1.2.0** - Веб-интерфейс (планируется)
- **v2.0.0** - Поддержка других СУБД (планируется)

---

**Автор:** asneg-zz  
**Версия:** 1.0.0  
**Дата обновления:** 2025  

⭐ **Если проект оказался полезным, поставьте звездочку на GitHub!**