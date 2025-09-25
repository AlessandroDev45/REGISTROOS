#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criar usuários da Mecânica diretamente no banco de dados
"""

import sqlite3
import hashlib
from datetime import datetime

def hash_password(password):
    """Cria hash da senha usando bcrypt-like"""
    # Simulação simples do hash - em produção usar bcrypt
    return hashlib.sha256(password.encode()).hexdigest()

def criar_usuarios_mecanica():
    """Cria usuários da Mecânica diretamente no banco"""
    print("🏭 CRIANDO USUÁRIOS DA MECÂNICA DIRETAMENTE NO BANCO")
    print("=" * 60)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect('RegistroOS/registrooficial/backend/registroos.db')
        cursor = conn.cursor()
        
        # Buscar ID do setor Mecânica
        cursor.execute("SELECT id, nome, departamento FROM tipo_setores WHERE nome LIKE '%MECANICA%'")
        setor_mecanica = cursor.fetchone()
        
        if not setor_mecanica:
            print("❌ Setor Mecânica não encontrado")
            return False
        
        setor_id, setor_nome, departamento = setor_mecanica
        print(f"✅ Setor encontrado: {setor_nome} (ID: {setor_id}) - {departamento}")
        
        # Buscar ID do departamento
        cursor.execute("SELECT id FROM tipo_departamentos WHERE nome = ?", (departamento,))
        dept_result = cursor.fetchone()
        dept_id = dept_result[0] if dept_result else 1
        
        # Usuários para criar
        usuarios = [
            {
                "nome_completo": "João Silva Mecânico",
                "nome_usuario": "joao.mecanica",
                "email": "joao.mecanica@registroos.com",
                "matricula": "MEC001",
                "setor": setor_nome,
                "departamento": departamento,
                "cargo": "Supervisor de Mecânica",
                "privilege_level": "SUPERVISOR",
                "trabalha_producao": True
            },
            {
                "nome_completo": "Maria Santos Montadora",
                "nome_usuario": "maria.mecanica",
                "email": "maria.mecanica@registroos.com",
                "matricula": "MEC002",
                "setor": setor_nome,
                "departamento": departamento,
                "cargo": "Técnica Mecânica",
                "privilege_level": "USER",
                "trabalha_producao": True
            },
            {
                "nome_completo": "Pedro Costa Mecânico",
                "nome_usuario": "pedro.mecanica",
                "email": "pedro.mecanica@registroos.com",
                "matricula": "MEC003",
                "setor": setor_nome,
                "departamento": departamento,
                "cargo": "Mecânico Montador",
                "privilege_level": "USER",
                "trabalha_producao": True
            },
            {
                "nome_completo": "Ana Oliveira Técnica",
                "nome_usuario": "ana.mecanica",
                "email": "ana.mecanica@registroos.com",
                "matricula": "MEC004",
                "setor": setor_nome,
                "departamento": departamento,
                "cargo": "Técnica de Montagem",
                "privilege_level": "USER",
                "trabalha_producao": True
            }
        ]
        
        usuarios_criados = 0
        senha_hash = hash_password("123456")
        data_atual = datetime.now().isoformat()
        
        for usuario in usuarios:
            try:
                # Verificar se usuário já existe
                cursor.execute("SELECT id FROM tipo_usuarios WHERE email = ?", (usuario["email"],))
                if cursor.fetchone():
                    print(f"   ⚠️ Usuário {usuario['nome_completo']} já existe")
                    continue
                
                # Inserir usuário
                cursor.execute("""
                    INSERT INTO tipo_usuarios (
                        nome_completo, nome_usuario, email, matricula, senha_hash,
                        setor, departamento, cargo, privilege_level, trabalha_producao,
                        is_approved, primeiro_login, id_setor, id_departamento,
                        data_criacao, data_ultima_atualizacao
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    usuario["nome_completo"],
                    usuario["nome_usuario"],
                    usuario["email"],
                    usuario["matricula"],
                    senha_hash,
                    usuario["setor"],
                    usuario["departamento"],
                    usuario["cargo"],
                    usuario["privilege_level"],
                    usuario["trabalha_producao"],
                    True,  # is_approved
                    True,  # primeiro_login
                    setor_id,
                    dept_id,
                    data_atual,
                    data_atual
                ))
                
                usuarios_criados += 1
                print(f"   ✅ Criado: {usuario['nome_completo']} ({usuario['privilege_level']})")
                
            except Exception as e:
                print(f"   ❌ Erro ao criar {usuario['nome_completo']}: {e}")
        
        # Commit das mudanças
        conn.commit()
        
        # Verificar usuários criados
        cursor.execute("SELECT nome_completo, email, privilege_level, setor FROM tipo_usuarios WHERE setor LIKE '%MECANICA%'")
        usuarios_mecanica = cursor.fetchall()
        
        print(f"\n📊 RESUMO:")
        print(f"   ✅ Usuários criados: {usuarios_criados}")
        print(f"   📋 Total usuários Mecânica: {len(usuarios_mecanica)}")
        
        print(f"\n👥 USUÁRIOS DA MECÂNICA:")
        for user in usuarios_mecanica:
            nome, email, nivel, setor = user
            print(f"   - {nome} ({nivel})")
            print(f"     📧 {email} | 🏭 {setor}")
        
        conn.close()
        
        print(f"\n🎉 USUÁRIOS DA MECÂNICA CRIADOS COM SUCESSO!")
        print(f"   🔑 Senha padrão para todos: 123456")
        print(f"   📋 Todos aprovados e prontos para uso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuários: {e}")
        return False

def main():
    """Função principal"""
    sucesso = criar_usuarios_mecanica()
    
    if sucesso:
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("   1. Execute: python fluxo_completo_mecanica.py")
        print("   2. Teste login com qualquer usuário criado")
        print("   3. Senha: 123456")
    else:
        print("\n❌ FALHA NA CRIAÇÃO DOS USUÁRIOS")
        print("   Verifique o banco de dados e tente novamente")

if __name__ == "__main__":
    main()
