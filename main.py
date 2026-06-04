import requests
from pprint import pprint


url = 'https://career.habr.com/api/frontend/vacancies'
# https://career.habr.com/api/frontend/vacancies?locations[]=c678 --запрос по городу Москва

params = {
    'locations[]':'c_678',
    'page':'1',
    'per_page':'2'
}

headers = {
    'User-Agent': 'PetProject/1.0'
}

response = requests.get(url, params=params, headers=headers)

print(response.status_code)
pprint(response.json())
