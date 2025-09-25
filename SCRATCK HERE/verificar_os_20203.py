#!/usr/bin/env python3
"""
Script para verificar se a OS 20203 existe no banco
"""

import sqlite3

def verificar_os_20203():
    """Verifica se a OS 20203 existe no banco"""
    
    print("🔍 VERIFICANDO OS 20203 NO BANCO")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar OS 20203
        print("📋 BUSCANDO OS 20203...")
        cursor.execute("SELECT * FROM ordens_servico WHERE os_numero = ? OR os_numero = ?", ("20203", "000020203"))
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"✅ OS 20203 ENCONTRADA!")
            print(f"   ID: {resultado[0]}")
            print(f"   Número: {resultado[1]}")
            print(f"   Status: {resultado[2] if len(resultado) > 2 else 'N/A'}")
        else:
            print(f"❌ OS 20203 NÃO ENCONTRADA")
        
        # Buscar todas as OSs que começam com 202
        print(f"\n📋 BUSCANDO OSs QUE COMEÇAM COM 202...")
        cursor.execute("SELECT os_numero, status_os FROM ordens_servico WHERE os_numero LIKE '202%' OR os_numero LIKE '%202%' LIMIT 10")
        resultados = cursor.fetchall()
        
        if resultados:
            print(f"✅ {len(resultados)} OSs encontradas:")
            for i, (numero, status) in enumerate(resultados, 1):
                print(f"   {i}. {numero} - {status}")
        else:
            print(f"❌ Nenhuma OS encontrada com 202")
        
        # Contar total de OSs
        cursor.execute("SELECT COUNT(*) FROM ordens_servico")
        total = cursor.fetchone()[0]
        print(f"\n📊 TOTAL DE OSs NO BANCO: {total}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar OS: {e}")

if __name__ == "__main__":
    verificar_os_20203()
