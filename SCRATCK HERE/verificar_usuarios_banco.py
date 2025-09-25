#!/usr/bin/env python3
"""
Verificar usuários no banco de dados
"""

import sqlite3

def verificar_usuarios():
    conn = sqlite3.connect('C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db')
    cursor = conn.cursor()

    print('🔍 Verificando usuários no banco...')

    # Verificar usuários
    cursor.execute('SELECT id, nome_completo, email, nome_usuario, privilege_level, is_approved FROM tipo_usuarios LIMIT 15')
    usuarios = cursor.fetchall()

    print(f'📋 Encontrados {len(usuarios)} usuários:')
    for user in usuarios:
        print(f'  ID: {user[0]}, Nome: {user[1]}, Email: {user[2]}, Username: {user[3]}, Privilege: {user[4]}, Aprovado: {user[5]}')

    # Verificar se existe admin
    cursor.execute('SELECT * FROM tipo_usuarios WHERE privilege_level = "ADMIN" OR email LIKE "%admin%"')
    admins = cursor.fetchall()
    
    print(f'\n🔑 Usuários admin encontrados: {len(admins)}')
    for admin in admins:
        print(f'  ID: {admin[0]}, Email: {admin[3]}, Username: {admin[4]}, Aprovado: {admin[12]}')

    conn.close()

if __name__ == "__main__":
    verificar_usuarios()
