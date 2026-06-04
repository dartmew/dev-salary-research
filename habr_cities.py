import requests
import json
import os


URL = 'https://career.habr.com/api/frontend/suggestions/locations'
HEADERS = {
    'User-Agent': 'PetProject/1.0'
}
CACHE_FILE = 'cities_cache.json'


def save_cities_to_cache(cities_dict):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cities_dict, f, ensure_ascii=False, indent=2)
    print(f'Saved as {CACHE_FILE}')


def load_cities_from_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def load_cities(use_cache=True):
    if use_cache:
        cached = load_cities_from_cache()
        if cached:
            print('Loading by cache')
            return cached
        
    print('Loading by API')
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    cities_list = data.get('list', [])

    if not cities_list:
        raise ValueError('No cities found in response')
    cities_dict = {
        'by_code': {item['value']: item['title'] for item in data['list']},
        'by_title': {item['title']: item['value'] for item in data['list']}
    }
    save_cities_to_cache(cities_dict)
    return cities_dict


def get_city_name(code, cities = None):
    if cities is None:
        cities = load_cities()
    return cities['by_code'].get(code, f'Unknown code: {code}')


def get_city_code(title, cities = None):
    if cities is None:
        cities = load_cities()
    return cities['by_title'].get(title, f'Unknown city: {title}')


def search_city_by_name(partial_title, cities=None):
    if cities is None:
        cities = load_cities()
    partial_lower = partial_title.lower()
    matches = [
        (code, name)
        for code, name in cities['by_code'].items()
        if partial_lower in name.lower()
    ]
    return matches
