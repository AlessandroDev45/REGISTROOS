#!/usr/bin/env python3
"""
Script para adicionar subcategorias na tabela tipos_maquina
"""

import sqlite3

def adicionar_subcategorias():
    """Adiciona subcategorias para os tipos de máquina existentes"""
    
    print("🔧 ADICIONANDO SUBCATEGORIAS NA TABELA tipos_maquina")
    print("=" * 60)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect("RegistroOS/registrooficial/backend/registroos_new.db")
        cursor = conn.cursor()
        
        # Mapeamento de categorias para subcategorias
        subcategorias_map = {
            'MOTOR CA': 'Estator,Rotor,Rolamentos,Ventilação,Carcaça',
            'MOTOR CC': 'Campo Shunt,Campo Série,Interpolos,Armadura,Escovas,Comutador',
            'GERADOR CA': 'Estator,Rotor,Excitatriz,Rolamentos,Ventilação',
            'TRANSFORMADOR': 'Núcleo,Bobinas,Isolação,Óleo Isolante,Buchas'
        }
        
        # Verificar dados atuais
        print("1️⃣ Dados atuais:")
        cursor.execute("SELECT id, nome_tipo, categoria, subcategoria FROM tipos_maquina ORDER BY categoria")
        dados_atuais = cursor.fetchall()
        
        for row in dados_atuais:
            print(f"   ID: {row[0]}, Nome: {row[1]}, Categoria: {row[2]}, Subcategoria: {row[3]}")
        
        # Atualizar subcategorias baseadas na categoria
        print(f"\n2️⃣ Atualizando subcategorias...")
        
        updates_realizados = 0
        
        for categoria, subcategorias in subcategorias_map.items():
            # Atualizar registros que têm essa categoria mas não têm subcategoria
            cursor.execute("""
                UPDATE tipos_maquina 
                SET subcategoria = ? 
                WHERE categoria = ? AND (subcategoria IS NULL OR subcategoria = '')
            """, (subcategorias, categoria))
            
            rows_affected = cursor.rowcount
            if rows_affected > 0:
                print(f"   ✅ {categoria}: {rows_affected} registro(s) atualizado(s)")
                updates_realizados += rows_affected
            else:
                print(f"   ℹ️ {categoria}: Nenhum registro para atualizar")
        
        # Commit das mudanças
        conn.commit()
        
        # Verificar dados após atualização
        print(f"\n3️⃣ Dados após atualização:")
        cursor.execute("""
            SELECT id, nome_tipo, categoria, subcategoria 
            FROM tipos_maquina 
            WHERE subcategoria IS NOT NULL AND subcategoria != ''
            ORDER BY categoria
        """)
        dados_atualizados = cursor.fetchall()
        
        for row in dados_atualizados:
            print(f"   ID: {row[0]}, Nome: {row[1]}, Categoria: {row[2]}, Subcategoria: {row[3]}")
        
        conn.close()
        
        print(f"\n📊 RESUMO:")
        print(f"- Total de atualizações: {updates_realizados}")
        print(f"- Registros com subcategorias: {len(dados_atualizados)}")
        
        if updates_realizados > 0:
            print(f"\n✅ Subcategorias adicionadas com sucesso!")
            print(f"🔧 Agora teste novamente o frontend - as subcategorias devem aparecer")
        else:
            print(f"\nℹ️ Nenhuma atualização necessária")
        
    except Exception as e:
        print(f"❌ Erro ao adicionar subcategorias: {e}")

def main():
    """Função principal"""
    adicionar_subcategorias()

if __name__ == "__main__":
    main()
