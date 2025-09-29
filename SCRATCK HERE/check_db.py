import sqlite3

# Conectar ao banco
conn = sqlite3.connect('RegistroOS/registrooficial/backend/registroos_new.db')
cursor = conn.cursor()

# Verificar estrutura das tabelas
print("=== ESTRUTURA tipo_departamentos ===")
cursor.execute('PRAGMA table_info(tipo_departamentos)')
for row in cursor.fetchall():
    print(row)

print("\n=== ESTRUTURA tipo_setores ===")
cursor.execute('PRAGMA table_info(tipo_setores)')
for row in cursor.fetchall():
    print(row)

# Verificar dados
print("\n=== DADOS tipo_departamentos ===")
cursor.execute('SELECT * FROM tipo_departamentos LIMIT 5')
for row in cursor.fetchall():
    print(row)

print("\n=== DADOS tipo_setores ===")
cursor.execute('SELECT * FROM tipo_setores LIMIT 5')
for row in cursor.fetchall():
    print(row)

conn.close()
