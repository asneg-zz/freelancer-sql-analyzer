import sqlite3
import pandas as pd
import os
import time
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from authorization import authorization_gigachat
from prompt_builder import PromptBuilder
from sql_utils import extract_sql_query, execute_sql_safely, compare_sql_queries
from test_questions_and_queries import TEST_CASES, TEST_CATEGORIES


class SQLTester:
    """Класс для тестирования генерации SQL запросов"""

    def __init__(self, db_path='freelancer_earnings.db', table_name='freelancer_earnings'):
        self.db_path = db_path
        self.table_name = table_name
        self.conn = None
        self.giga = None
        self.prompt_builder = None
        self.test_results = []

    def setup(self):
        """Инициализация всех компонентов"""
        print("🔧 Инициализация тестовой системы...")

        # Проверяем наличие CSV файла
        if not os.path.exists('freelancer_earnings_bd.csv'):
            print("❌ Файл freelancer_earnings_bd.csv не найден!")
            return False

        # Создаем/подключаемся к БД
        self.conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_csv('freelancer_earnings_bd.csv')
            df.to_sql(self.table_name, self.conn, if_exists='replace', index=False)
            print(f"✅ База данных готова. Загружено {len(df)} записей.")
        except Exception as e:
            print(f"❌ Ошибка при загрузке данных: {e}")
            return False

        # Инициализируем PromptBuilder
        self.prompt_builder = PromptBuilder(self.db_path, self.table_name)
        if not self.prompt_builder.analyze_and_prepare():
            print("❌ Не удалось проанализировать таблицу")
            return False

        # Инициализируем GigaChat
        try:
            self.giga = authorization_gigachat()
            print("✅ GigaChat подключен")
        except Exception as e:
            print(f"❌ Ошибка подключения к GigaChat: {e}")
            return False

        return True

    def run_single_test(self, test_case):
        """Выполняет один тест"""
        print(f"\n📝 Тест #{test_case['id']}: {test_case['question']}")

        # Создаем системный промт
        system_prompt = self.prompt_builder.build_enhanced_system_prompt()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=test_case['question'])
        ]

        start_time = time.time()

        try:
            # Отправляем запрос к GigaChat
            response = self.giga.invoke(messages)

            # Извлекаем SQL
            generated_sql = extract_sql_query(response.content)
            execution_time = time.time() - start_time

            if not generated_sql:
                return self._create_result(test_case, None, 'no_sql_extracted',
                                           execution_time, 'Не удалось извлечь SQL', response.content)

            # Проверяем выполнение SQL
            expected_success, expected_result, _ = execute_sql_safely(self.conn, test_case['expected_sql'])
            generated_success, generated_result, _ = execute_sql_safely(self.conn, generated_sql)

            # Сравниваем запросы
            similarity_type, similarity_score = compare_sql_queries(
                generated_sql, test_case['expected_sql'], self.table_name
            )

            if generated_success:
                status = 'success'
                error = None
            else:
                status = 'sql_error'
                error = generated_result

            return self._create_result(test_case, generated_sql, status,
                                       execution_time, error, response.content,
                                       similarity_score, similarity_type)

        except Exception as e:
            return self._create_result(test_case, None, 'exception',
                                       time.time() - start_time, str(e))

    def _create_result(self, test_case, generated_sql, status, execution_time,
                       error=None, raw_response='', similarity_score=0, similarity_type=''):
        """Создает словарь с результатом теста"""
        return {
            'test_id': test_case['id'],
            'question': test_case['question'],
            'category': test_case['category'],
            'expected_sql': test_case['expected_sql'],
            'generated_sql': generated_sql,
            'status': status,
            'similarity_score': similarity_score,
            'similarity_type': similarity_type,
            'execution_time': execution_time,
            'error': error,
            'raw_response': raw_response
        }

    def run_all_tests(self, test_cases=None):
        """Запускает все тесты"""
        if test_cases is None:
            test_cases = TEST_CASES

        print(f"\n🚀 Запуск {len(test_cases)} тестов...")
        print("=" * 70)

        self.test_results = []

        for i, test_case in enumerate(test_cases, 1):
            print(f"\nПрогресс: {i}/{len(test_cases)}")
            result = self.run_single_test(test_case)
            self.test_results.append(result)

            # Показываем результат теста
            self._print_test_result(result)

            # Пауза между запросами
            time.sleep(1)

        return self.test_results

    def _print_test_result(self, result):
        """Выводит результат теста"""
        if result['status'] == 'success':
            print(f"✅ Успех (сходство: {result['similarity_score']:.1f}%)")
        elif result['status'] == 'sql_error':
            print(f"❌ Ошибка SQL: {result.get('error', 'Неизвестная ошибка')}")
        elif result['status'] == 'no_sql_extracted':
            print(f"⚠️ Не извлечен SQL")
        else:
            print(f"💥 Исключение: {result.get('error', 'Неизвестная ошибка')}")

    def generate_report(self):
        """Генерирует отчет о тестировании"""
        if not self.test_results:
            print("❌ Нет результатов тестирования")
            return

        print("\n" + "=" * 70)
        print("📊 ОТЧЕТ О ТЕСТИРОВАНИИ")
        print("=" * 70)

        # Общая статистика
        total = len(self.test_results)
        by_status = {}
        for result in self.test_results:
            status = result['status']
            by_status[status] = by_status.get(status, 0) + 1

        print(f"Всего тестов: {total}")
        print(f"✅ Успешных: {by_status.get('success', 0)} ({by_status.get('success', 0) / total * 100:.1f}%)")
        print(f"❌ Ошибки SQL: {by_status.get('sql_error', 0)} ({by_status.get('sql_error', 0) / total * 100:.1f}%)")
        print(
            f"⚠️ Не извлечен SQL: {by_status.get('no_sql_extracted', 0)} ({by_status.get('no_sql_extracted', 0) / total * 100:.1f}%)")
        print(f"💥 Исключения: {by_status.get('exception', 0)} ({by_status.get('exception', 0) / total * 100:.1f}%)")

        # Статистика по категориям
        self._print_category_stats()

        # Средние показатели
        self._print_average_metrics()

        # Детали неуспешных тестов
        self._print_failed_tests()

        # Дополнительный анализ
        self._print_error_analysis()
        self._print_success_patterns()

    def _print_category_stats(self):
        """Выводит детализированную статистику по категориям с информацией об ошибках"""
        print(f"\n📈 ДЕТАЛИЗИРОВАННАЯ СТАТИСТИКА ПО КАТЕГОРИЯМ:")

        category_stats = {}
        category_errors = {}

        # Собираем статистику и ошибки по категориям
        for result in self.test_results:
            cat = result['category']
            test_id = result['test_id']
            status = result['status']

            if cat not in category_stats:
                category_stats[cat] = {'total': 0, 'success': 0, 'failed_tests': []}
                category_errors[cat] = {'sql_error': 0, 'no_sql_extracted': 0, 'exception': 0}

            category_stats[cat]['total'] += 1

            if status == 'success':
                category_stats[cat]['success'] += 1
            else:
                # Записываем информацию о неудачном тесте
                category_stats[cat]['failed_tests'].append({
                    'test_id': test_id,
                    'status': status,
                    'question': result['question'][:50] + "..." if len(result['question']) > 50 else result['question']
                })

                # Подсчитываем типы ошибок
                if status in category_errors[cat]:
                    category_errors[cat][status] += 1

        # Выводим статистику
        perfect_categories = []
        problematic_categories = []

        for category, stats in sorted(category_stats.items()):
            success_rate = stats['success'] / stats['total'] * 100
            cat_name = TEST_CATEGORIES.get(category, category)

            if success_rate == 100.0:
                perfect_categories.append((cat_name, stats))
                print(f"  ✅ {cat_name}: {stats['success']}/{stats['total']} (100.0%)")
            else:
                problematic_categories.append((cat_name, stats, category_errors[category]))
                print(f"  ❌ {cat_name}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")

        # Детализация проблемных категорий
        if problematic_categories:
            print(f"\n🚨 ДЕТАЛИ ОШИБОК ПО ПРОБЛЕМНЫМ КАТЕГОРИЯМ:")

            for cat_name, stats, errors in problematic_categories:
                print(f"\n📋 {cat_name}:")

                # Типы ошибок
                error_types = []
                for error_type, count in errors.items():
                    if count > 0:
                        error_names = {
                            'sql_error': 'Ошибки SQL выполнения',
                            'no_sql_extracted': 'Не извлечен SQL',
                            'exception': 'Исключения системы'
                        }
                        error_types.append(f"{error_names.get(error_type, error_type)}: {count}")

                if error_types:
                    print(f"    Типы ошибок: {', '.join(error_types)}")

                # Список неудачных тестов
                print(f"    Неудачные тесты:")
                for failed_test in stats['failed_tests']:
                    status_icons = {
                        'sql_error': '🔴',
                        'no_sql_extracted': '🟡',
                        'exception': '💥'
                    }
                    icon = status_icons.get(failed_test['status'], '❓')
                    print(f"      {icon} Тест #{failed_test['test_id']}: {failed_test['question']}")

        # Сводка
        total_categories = len(category_stats)
        perfect_count = len(perfect_categories)

        print(f"\n📊 СВОДКА:")
        print(f"  Всего категорий: {total_categories}")
        print(f"  Идеальных категорий (100%): {perfect_count}")
        print(f"  Проблемных категорий: {len(problematic_categories)}")

        if perfect_count == total_categories:
            print(f"  🎉 ВСЕ КАТЕГОРИИ РАБОТАЮТ ИДЕАЛЬНО!")
        else:
            print(f"  ⚠️  Требуется внимание к {len(problematic_categories)} категориям")

    def _print_average_metrics(self):
        """Выводит средние метрики"""
        successful_results = [r for r in self.test_results if r['status'] == 'success']

        if successful_results:
            avg_similarity = sum(r['similarity_score'] for r in successful_results) / len(successful_results)
            avg_time = sum(r['execution_time'] for r in successful_results) / len(successful_results)

            print(f"\n⚡ СРЕДНИЕ ПОКАЗАТЕЛИ:")
            print(f"  Средняя схожесть SQL: {avg_similarity:.1f}%")
            print(f"  Среднее время выполнения: {avg_time:.2f}с")

            # Дополнительный анализ схожести
            if avg_similarity < 85:
                print(f"  💡 Примечание: Схожесть {avg_similarity:.1f}% означает, что система генерирует")
                print(f"     функционально правильные, но синтаксически различающиеся SQL запросы")

    def _print_failed_tests(self):
        """Выводит детали неуспешных тестов"""
        failed_tests = [r for r in self.test_results if r['status'] != 'success']

        if failed_tests:
            print(f"\n❌ ДЕТАЛИ НЕУСПЕШНЫХ ТЕСТОВ:")
            for result in failed_tests:
                print(f"\nТест #{result['test_id']}: {result['question']}")
                print(f"  Статус: {result['status']}")
                if result.get('error'):
                    print(f"  Ошибка: {result['error']}")
                if result.get('generated_sql'):
                    print(f"  Сгенерированный SQL: {result['generated_sql']}")
                print(f"  Ожидаемый SQL: {result['expected_sql']}")

    def _print_error_analysis(self):
        """Дополнительный метод для анализа типов ошибок"""
        print(f"\n🔍 АНАЛИЗ ТИПОВ ОШИБОК:")

        error_analysis = {}
        for result in self.test_results:
            if result['status'] != 'success':
                status = result['status']
                if status not in error_analysis:
                    error_analysis[status] = []
                error_analysis[status].append(result)

        if not error_analysis:
            print("  ✅ Ошибок не обнаружено!")
            return

        for error_type, failed_tests in error_analysis.items():
            error_names = {
                'sql_error': '🔴 Ошибки выполнения SQL',
                'no_sql_extracted': '🟡 Не удалось извлечь SQL',
                'exception': '💥 Системные исключения'
            }

            print(f"\n{error_names.get(error_type, error_type)} ({len(failed_tests)} тестов):")

            for test in failed_tests:
                print(f"  • Тест #{test['test_id']}: {test['question']}")
                if test.get('error'):
                    print(f"    Ошибка: {test['error'][:100]}...")
                if test.get('generated_sql'):
                    print(f"    SQL: {test['generated_sql'][:80]}...")

    def _print_success_patterns(self):
        """Анализ паттернов успешных тестов"""
        print(f"\n🎯 АНАЛИЗ УСПЕШНЫХ ПАТТЕРНОВ:")

        successful_tests = [r for r in self.test_results if r['status'] == 'success']

        if not successful_tests:
            print("  ❌ Нет успешных тестов для анализа")
            return

        # Группируем по типам запросов
        query_patterns = {}
        for test in successful_tests:
            sql = test.get('generated_sql', '').upper()

            if 'GROUP BY' in sql:
                pattern = 'Группировка'
            elif 'COUNT(' in sql and 'CASE WHEN' in sql:
                pattern = 'Процентные расчеты'
            elif 'AVG(' in sql or 'MIN(' in sql or 'MAX(' in sql:
                pattern = 'Агрегация'
            elif 'WHERE' in sql and 'ORDER BY' in sql:
                pattern = 'Фильтрация с сортировкой'
            elif 'ORDER BY' in sql:
                pattern = 'Простая сортировка'
            else:
                pattern = 'Другое'

            if pattern not in query_patterns:
                query_patterns[pattern] = 0
            query_patterns[pattern] += 1

        print("  Успешные паттерны:")
        for pattern, count in sorted(query_patterns.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(successful_tests) * 100
            print(f"    • {pattern}: {count} тестов ({percentage:.1f}%)")

    def save_results_to_file(self, filename=None):
        """Сохраняет результаты в файл"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Результаты тестирования SQL генерации\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")

            for result in self.test_results:
                f.write(f"Тест #{result['test_id']}: {result['question']}\n")
                f.write(f"Категория: {result['category']}\n")
                f.write(f"Статус: {result['status']}\n")
                f.write(f"Ожидаемый SQL: {result['expected_sql']}\n")

                if result.get('generated_sql'):
                    f.write(f"Сгенерированный SQL: {result['generated_sql']}\n")
                if result.get('similarity_score'):
                    f.write(f"Схожесть: {result['similarity_score']:.1f}%\n")
                if result.get('execution_time'):
                    f.write(f"Время выполнения: {result['execution_time']:.2f}с\n")
                if result.get('error'):
                    f.write(f"Ошибка: {result['error']}\n")

                f.write("-" * 50 + "\n")

        print(f"\n💾 Результаты сохранены в файл: {filename}")

    def cleanup(self):
        """Очистка ресурсов"""
        if self.conn:
            self.conn.close()


def main():
    """Основная функция тестирования"""
    print("🧪 СИСТЕМА ТЕСТИРОВАНИЯ SQL ГЕНЕРАЦИИ")
    print("=" * 70)

    tester = SQLTester()

    # Инициализация
    if not tester.setup():
        print("❌ Не удалось инициализировать тестовую систему")
        return

    try:
        # Запуск тестов
        tester.run_all_tests()

        # Генерация отчета
        tester.generate_report()

        # Сохранение результатов
        save_results = input("\nСохранить результаты в файл? (y/n): ").lower()
        if save_results == 'y':
            tester.save_results_to_file()

        # Опция запуска отдельных тестов
        while True:
            test_input = input("\nЗапустить конкретный тест? Введите номер или 'q' для выхода: ").strip()
            if test_input.lower() == 'q':
                break

            try:
                test_id = int(test_input)
                test_case = next((t for t in TEST_CASES if t['id'] == test_id), None)

                if test_case:
                    result = tester.run_single_test(test_case)
                    print(f"\nРезультат теста #{test_id}:")
                    print(f"Ожидаемый SQL: {result['expected_sql']}")
                    print(f"Сгенерированный SQL: {result.get('generated_sql', 'Не извлечен')}")
                    print(f"Статус: {result['status']}")
                    if result.get('similarity_score'):
                        print(f"Схожесть: {result['similarity_score']:.1f}%")
                else:
                    print(f"❌ Тест с номером {test_id} не найден")
            except ValueError:
                print("❌ Введите корректный номер теста")

    except KeyboardInterrupt:
        print("\n\n⏹️ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
    finally:
        tester.cleanup()
        print("\n👋 Тестирование завершено!")


if __name__ == "__main__":
    main()