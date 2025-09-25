#!/usr/bin/env python3
"""
Verificar se a OS 12345 existe no banco
"""

import sqlite3

def verificar_os_12345():
    """Verifica se a OS 12345 existe no banco"""
    try:
        db_path = 'C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verificando OS 12345 no banco...")
        
        # Buscar OS 12345
        cursor.execute("SELECT * FROM ordens_servico WHERE os_numero = ? OR os_numero = ?", ("12345", "000012345"))
        result = cursor.fetchone()
        
        if result:
            print("✅ OS 12345 ENCONTRADA no banco!")
            print(f"   ID: {result[0]}")
            print(f"   OS Número: {result[1]}")
            print(f"   Status: {result[2]}")
            print(f"   Descrição: {result[3] if len(result) > 3 else 'N/A'}")
            
            # Verificar cliente relacionado
            if len(result) > 52 and result[52]:
                cursor.execute("SELECT razao_social FROM clientes WHERE id = ?", (result[52],))
                cliente = cursor.fetchone()
                if cliente:
                    print(f"   Cliente: {cliente[0]}")
            
            # Verificar equipamento relacionado
            if len(result) > 53 and result[53]:
                cursor.execute("SELECT descricao FROM equipamentos WHERE id = ?", (result[53],))
                equipamento = cursor.fetchone()
                if equipamento:
                    print(f"   Equipamento: {equipamento[0]}")
                    
        else:
            print("❌ OS 12345 NÃO ENCONTRADA no banco")
            
            # Verificar se existe alguma OS similar
            cursor.execute("SELECT os_numero FROM ordens_servico WHERE os_numero LIKE '%12345%'")
            similares = cursor.fetchall()
            
            if similares:
                print("🔍 OSs similares encontradas:")
                for os_sim in similares:
                    print(f"   - {os_sim[0]}")
            else:
                print("   Nenhuma OS similar encontrada")
        
        conn.close()
        return result is not None
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

def verificar_cliente_air_liquide():
    """Verifica se o cliente AIR LIQUIDE já existe"""
    try:
        db_path = 'C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 Verificando cliente AIR LIQUIDE...")
        
        # Buscar por CNPJ ou nome
        cursor.execute("SELECT * FROM clientes WHERE cnpj_cpf = ? OR razao_social LIKE ?", 
                      ("00.331.788/0066-64", "%AIR LIQUIDE%"))
        result = cursor.fetchone()
        
        if result:
            print("✅ Cliente AIR LIQUIDE ENCONTRADO!")
            print(f"   ID: {result[0]}")
            print(f"   Razão Social: {result[1]}")
            print(f"   CNPJ: {result[3]}")
        else:
            print("❌ Cliente AIR LIQUIDE NÃO ENCONTRADO")
        
        conn.close()
        return result is not None
        
    except Exception as e:
        print(f"❌ Erro ao verificar cliente: {e}")
        return False

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO DA OS 12345 NO BANCO")
    print("=" * 40)
    
    os_existe = verificar_os_12345()
    cliente_existe = verificar_cliente_air_liquide()
    
    print("\n" + "=" * 40)
    print("📊 RESULTADO:")
    print(f"   OS 12345 existe: {'✅' if os_existe else '❌'}")
    print(f"   Cliente existe: {'✅' if cliente_existe else '❌'}")
    
    if not os_existe:
        print("\n🎯 PERFEITO PARA TESTE!")
        print("   A OS 12345 não existe no banco")
        print("   Posso testar a criação automática")
    else:
        print("\n⚠️ OS JÁ EXISTE!")
        print("   Vou usar outra OS para teste")

if __name__ == "__main__":
    main()
