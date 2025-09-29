import sqlite3

conn = sqlite3.connect('RegistroOS/registrooficial/backend/registroos_new.db')
cursor = conn.cursor()

print('=== VERIFICAÇÃO DE USUÁRIOS ===')
cursor.execute('SELECT id, email, nome_completo, privilege_level FROM tipo_usuarios WHERE privilege_level = "ADMIN" LIMIT 5')
users = cursor.fetchall()
print('Usuários ADMIN:')
for user in users:
    print(f'   - ID: {user[0]}, Email: {user[1]}, Nome: {user[2]}, Privilege: {user[3]}')

conn.close()
