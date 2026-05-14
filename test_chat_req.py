import requests
import random
import string

BASE_URL = 'https://bitirme-g5gn.onrender.com'

def test():
    email = ''.join(random.choices(string.ascii_lowercase, k=10)) + '@test.com'
    password = 'password123'
    requests.post(f'{BASE_URL}/users/', json={'email': email, 'password': password})
    res = requests.post(f'{BASE_URL}/auth/login', json={'email': email, 'password': password})
    
    if res.status_code == 200:
        token = res.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        chat_req = {
            'user_id': 0,
            'user_message': 'Su ybegin kalori ve makro degerlerini hesapla, sadece JSON formatinda dondur (baska hicbir sey yazma): {"food_name": "...", "calories": 0, "protein": 0, "fat": 0, "carbs": 0}\n\nYemek: 1 avuc tuzlu badem',
            'history': '',
            'boy_cm': 170.0,
            'kilo_kg': 70.0,
            'yas': 25,
            'cinsiyet': 'Belirtilmemis',
            'bugunku_ogunler': []
        }
        print('Testing /chat...')
        chat_res = requests.post(f'{BASE_URL}/chat', json=chat_req, headers=headers)
        print('Status:', chat_res.status_code)
        print('Response:', chat_res.text)
    else:
        print('Login failed', res.status_code)

if __name__ == '__main__':
    test()
