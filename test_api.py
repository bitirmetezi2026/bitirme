import requests
import string
import random

BASE_URL = 'https://bitirme-g5gn.onrender.com'

def test_api():
    email = ''.join(random.choices(string.ascii_lowercase, k=10)) + '@test.com'
    password = 'password123'

    res = requests.post(f'{BASE_URL}/users/', json={'email': email, 'password': password})

    res = requests.post(f'{BASE_URL}/auth/login', json={'email': email, 'password': password})
    print('Login:', res.status_code)
    
    if res.status_code == 200:
        token = res.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        
        ex_data = {'exercise_type': 'Kosu', 'minutes': 30, 'calories_burned': 200.0}
        res2 = requests.post(f'{BASE_URL}/exercises/', json=ex_data, headers=headers)
        print('Save Exercise:', res2.status_code, res2.text)
        
        res3 = requests.get(f'{BASE_URL}/exercises/by-date/?date=2026-05-14', headers=headers)
        print('Get Exercises:', res3.status_code, res3.text)

test_api()