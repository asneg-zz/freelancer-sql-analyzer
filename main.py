import sqlite3
import pandas as pd
import os
from langchain_core.messages import HumanMessage, SystemMessage
from authorization import authorization_gigachat
from prompt_builder import PromptBuilder
from sql_utils import extract_sql_query, execute_sql_safely, format_sql_results


def create_database_and_load_data():
    """Создает базу данных SQLite и загружает данные из CSV файла"""
    if not os.path.exists('freelancer_earnings_bd.csv'):
        print("Ошибка: файл freelancer_earnings_bd.csv не найден!")
        return None

    conn = sqlite3.connect('freelancer_earnings.db')
    try:
        df = pd.read_csv('freelancer_earnings_bd.csv')
        df.to_sql('freelancer_earnings', conn, if_exists='replace', index=False)
        print(f"База данных создана. Загружено {len(df)} записей.")
        return conn
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        conn.close()
        return None


def main():
    # Создаем базу данных
    conn = create_database_and_load_data()
    if not conn:
        return

    # Используем PromptBuilder для анализа и создания промтов
    print("\nАнализирую структуру таблицы...")
    prompt_builder = PromptBuilder('freelancer_earnings.db', 'freelancer_earnings')

    if prompt_builder.analyze_and_prepare():
        print("✅ Анализ завершен успешно")
        print(prompt_builder.get_table_summary())
        enhanced_system_prompt = prompt_builder.build_enhanced_system_prompt()
        print("Системный промт обновлен с улучшениями")
    else:
        print("⚠️ Не удалось проанализировать таблицу, используется базовый промт")
        enhanced_system_prompt = prompt_builder.build_basic_system_prompt()

    # Инициализируем GigaChat
    try:
        giga = authorization_gigachat()
    except Exception as e:
        print(f"❌ Ошибка подключения к GigaChat: {e}")
        conn.close()
        return

    messages = [SystemMessage(content=enhanced_system_prompt)]

    print("\n" + "=" * 70)
    print("🚀 УЛУЧШЕННАЯ СИСТЕМА SQL-ЗАПРОСОВ ГОТОВА!")
    print("=" * 70)
    print("Введите ваш запрос или команду:")
    print("• 'help' - справка")
    print("• 'schema' - структура таблицы")
    print("• 'examples' - примеры запросов")
    print("• 'suggest <текст>' - умные предложения")
    print("• 'validate <текст>' - валидация запроса")
    print("• 'пока' - выход")
    print("-" * 70)

    while True:
        user_input = input("\n💬 Ваш запрос: ").strip()

        if user_input.lower() in ['пока', 'выход', 'exit', 'quit']:
            break

        if not user_input:
            continue

        # Обработка специальных команд
        if user_input.lower() in ['help', 'помощь']:
            print("""
📚 СПРАВКА:
• Задавайте вопросы на естественном языке
• Система автоматически создаст SQL запрос  
• Доступные команды: help, schema, examples, suggest, validate, пока
• Система знает все возможные значения в колонках
• Новые возможности: валидация запросов и умные предложения
            """)
            continue

        if user_input.lower() in ['schema', 'схема']:
            print("\n📋 СТРУКТУРА ТАБЛИЦЫ:")
            print(prompt_builder.analyzer.generate_prompt_schema())
            continue

        if user_input.lower() in ['examples', 'примеры']:
            suggestions = prompt_builder.get_improved_suggestions()
            print("\n💡 ПРИМЕРЫ ЗАПРОСОВ:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
            continue

        if user_input.lower().startswith('suggest '):
            query_text = user_input[8:]  # Убираем 'suggest '
            suggestions = prompt_builder.get_improved_suggestions(query_text)
            print(f"\n🎯 УМНЫЕ ПРЕДЛОЖЕНИЯ ДЛЯ '{query_text}':")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
            continue

        if user_input.lower().startswith('validate '):
            query_text = user_input[9:]  # Убираем 'validate '
            validation_result = prompt_builder.validate_and_suggest(query_text)

            print(f"\n🔍 ВАЛИДАЦИЯ ЗАПРОСА '{query_text}':")

            if validation_result['validation_passed']:
                print("✅ Запрос корректен")
            else:
                print("⚠️ ПРЕДУПРЕЖДЕНИЯ:")
                for warning in validation_result['warnings']:
                    print(f"  • {warning}")

            if validation_result['suggestions']:
                print("\n💡 РЕКОМЕНДУЕМЫЕ ЗАПРОСЫ:")
                for i, suggestion in enumerate(validation_result['suggestions'], 1):
                    print(f"  {i}. {suggestion}")
            continue

        # Валидация пользовательского ввода ПЕРЕД отправкой к GigaChat
        if prompt_builder.is_analyzed:
            validation_result = prompt_builder.validate_and_suggest(user_input)

            if not validation_result['validation_passed']:
                print("\n🔧 АВТОМАТИЧЕСКАЯ ОПТИМИЗАЦИЯ ЗАПРОСА:")
                for warning in validation_result['warnings']:
                    print(f"  • {warning}")

                if validation_result['suggestions']:
                    print("\n✅ ИСПОЛЬЗУЕТСЯ ОПТИМИЗИРОВАННЫЙ SQL:")
                    # Берем первый рекомендуемый запрос и используем его
                    recommended_query = validation_result['suggestions'][0]
                    print(f"  {recommended_query}")

                    # Заменяем пользовательский ввод на готовый SQL запрос
                    user_input = f"Выполни этот SQL запрос: {recommended_query}"
                    print("\n🚀 Запрос автоматически оптимизирован и готов к выполнению!")

        try:
            # Добавляем сообщение пользователя
            messages.append(HumanMessage(content=user_input))
            print("🤖 Анализирую запрос и создаю SQL...")

            # Получаем ответ от GigaChat
            response = giga.invoke(messages)
            messages.append(response)

            # Извлекаем SQL запрос
            sql_query = extract_sql_query(response.content)

            if sql_query:
                # Выполняем запрос
                success, results, columns = execute_sql_safely(conn, sql_query)

                # Форматируем и выводим результаты
                output = format_sql_results(success, results, columns, sql_query)
                print(output)

            else:
                print("❌ Не удалось извлечь SQL запрос из ответа.")
                print(f"🤖 Полный ответ: {response.content}")

        except Exception as e:
            print(f"❌ Ошибка при обработке запроса: {e}")

    # Статистика и завершение
    user_queries = len([m for m in messages if isinstance(m, HumanMessage)])
    print(f"\n📊 Обработано запросов: {user_queries}")
    conn.close()
    print("👋 До свидания!")


if __name__ == "__main__":
    main()