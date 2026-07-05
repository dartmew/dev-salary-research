import os
import requests
import time
from dotenv import load_dotenv
from terminaltables import AsciiTable


def build_language_stats(total_found, salaries):
    processed = len(salaries)
    average = None
    if processed > 0:
        average = int(sum(salaries) / processed)
    return {
        'vacancies_found': total_found,
        'vacancies_processed': processed,
        'average_salary': average,
    }


def predict_salary(salary_from, salary_to):
    if salary_from is not None and salary_to is not None:
        return (salary_from + salary_to) / 2.0
    elif salary_from is not None:
        return salary_from * 1.2
    elif salary_to is not None:
        return salary_to * 0.8
    else:
        return None


def predict_rub_salary_habr(vacancy):
    salary = vacancy.get('salary')

    if not salary:
        return None

    if salary.get('currency') != 'RUR':
        return None

    return predict_salary(salary.get('from'), salary.get('to'))


def fetch_habr_salaries(language, town_id='c_678'):
    url = 'https://career.habr.com/api/frontend/vacancies'
    all_salaries = []
    total_found = 0
    page = 1
    per_page = 100

    while True:
        params = {
            'q': f'разработчик {language}',
            'locations[]': town_id,
            'type': 'all',
            'per_page': per_page,
            'page': page
        }
        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            break

        data = resp.json()

        if page == 1:
            total_found = data.get('meta', {}).get('totalResults', 0)

            if total_found == 0:
                break

        for vac in data.get('list', []):
            rub = predict_rub_salary_habr(vac)

            if rub is not None:
                all_salaries.append(rub)

        total_pages = data.get('meta', {}).get('totalPages', 1)

        if page >= total_pages:
            break
        page += 1
        time.sleep(0.2)

    return total_found, all_salaries


def get_habr_statistics(languages, town_id='c_678'):
    stats = {}

    for lang in languages:
        print(f"  Habr: загрузка {lang}...")
        total, salaries = fetch_habr_salaries(lang, town_id)
        stats[lang] = build_language_stats(total, salaries)
        time.sleep(0.5)
    return stats


def predict_rub_salary_sj(vacancy):
    payment_from = vacancy.get('payment_from')
    payment_to = vacancy.get('payment_to')
    currency = vacancy.get('currency')

    if currency != 'rub':
        return None

    return predict_salary(payment_from, payment_to)


def fetch_sj_salaries(language, superjob_secret_key, town_id=4):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id': superjob_secret_key}
    all_salaries = []
    total_found = 0
    page = 0
    per_page = 100

    while True:
        params = {
            'keyword': f'разработчик {language}',
            'town': town_id,
            'page': page,
            'count': per_page
        }
        try:
            resp = requests.get(url, headers=headers, params=params)
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            break
        data = resp.json()

        if page == 0:
            total_found = data.get('total', 0)

            if total_found == 0:
                break

        for vac in data.get('objects', []):
            rub = predict_rub_salary_sj(vac)

            if rub is not None:
                all_salaries.append(rub)

        if not data.get('more', False):
            break
        page += 1
        time.sleep(0.3)

    return total_found, all_salaries


def get_sj_statistics(languages, superjob_secret_key, town_id=4):
    stats = {}

    for lang in languages:
        print(f"  SJ: загрузка {lang}...")
        total, salaries = fetch_sj_salaries(lang, superjob_secret_key, town_id)
        stats[lang] = build_language_stats(total, salaries)
        time.sleep(0.5)
    return stats


def print_statistics_table(stats, title):
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']
    ]

    for lang, data in sorted(stats.items(), key=lambda x: x[1]['vacancies_found'], reverse=True):
        lang_display = lang.lower()
        found = data['vacancies_found']
        processed = data['vacancies_processed']
        avg = data['average_salary']
        avg_str = str(avg) if avg is not None else '—'
        table_data.append([lang_display, found, processed, avg_str])
    table = AsciiTable(table_data, title=title)
    print(table.table)
    print()


def main():
    load_dotenv()
    superjob_secret_key = os.getenv('SUPERJOB_SECRET_KEY')

    languages = [
        'Python', 'Java', 'JavaScript', 'PHP', 'C++', 'C#',
        'C', 'Go', 'Ruby', 'Swift', 'TypeScript', 'Scala',
        'Objective-C', '1с'
    ]
    habr_town = 'c_678'
    sj_town = 4
    border_lengh = 70

    print("=" * border_lengh)
    print("Сбор статистики по зарплатам разработчиков в Москве")
    print("=" * border_lengh)

    print("\n--- HeadHunter ---")
    habr_stats = get_habr_statistics(languages, habr_town)

    print("\n--- SuperJob ---")
    if superjob_secret_key:  
        sj_stats = get_sj_statistics(languages, superjob_secret_key, sj_town)
    else:
        print('SuperJob ключ не найден, пропускаем.')
        sj_stats = {}

    print("\n" + "=" * border_lengh)
    print("ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print("=" * border_lengh)

    print_statistics_table(habr_stats, "Habr Moscow")
    print_statistics_table(sj_stats, "SuperJob Moscow")


if __name__ == '__main__':
    main()