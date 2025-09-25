#!/usr/bin/env python3
import requests

session = requests.Session()
session.post('http://localhost:8000/api/token', data={'username': 'admin@registroos.com', 'password': '123456'}, headers={'Content-Type': 'application/x-www-form-urlencoded'})
response = session.get('http://localhost:8000/api/usuarios/')
if response.status_code == 200:
    users = response.json()
    print('Usuários disponíveis:')
    for user in users:
        email = user.get('email', 'N/A')
        privilege = user.get('privilege_level', 'N/A')
        trabalha_prod = user.get('trabalha_producao', 'N/A')
        setor = user.get('setor', 'N/A')
        print(f'  - {email} ({privilege}) - Trabalha Produção: {trabalha_prod} - Setor: {setor}')
else:
    print(f'Erro: {response.status_code} - {response.text}')
