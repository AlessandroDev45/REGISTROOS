#!/usr/bin/env python3
import sqlite3

DB_PATH = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, email, nome_completo, privilege_level FROM tipo_usuarios WHERE privilege_level = "ADMIN"')
    admins = cursor.fetchall()
    
    print('Admins encontrados:')
    for admin in admins:
        print(f'  ID: {admin[0]}, Email: {admin[1]}, Nome: {admin[2]}, Privilege: {admin[3]}')
    
    conn.close()
    
except Exception as e:
    print(f"Erro: {e}")
