#!/usr/bin/env python3
import sqlite3

DB_PATH = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, nome, departamento FROM tipo_setores WHERE ativo = 1')
    setores = cursor.fetchall()
    
    print('Setores encontrados:')
    for setor in setores:
        nome_repr = repr(setor[1])  # Mostra caracteres especiais
        print(f'  ID: {setor[0]}, Nome: {nome_repr}, Departamento: {setor[2]}')
    
    # Verificar especificamente "MECANICA DIA"
    print('\nVerificando "MECANICA DIA":')
    cursor.execute('SELECT id, nome FROM tipo_setores WHERE nome = ? AND ativo = 1', ("MECANICA DIA",))
    result = cursor.fetchone()
    if result:
        print(f'  Encontrado: ID {result[0]}, Nome: {repr(result[1])}')
    else:
        print('  Não encontrado')
    
    conn.close()
    
except Exception as e:
    print(f"Erro: {e}")
