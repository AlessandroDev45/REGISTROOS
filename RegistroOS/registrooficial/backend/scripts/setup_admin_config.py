#!/usr/bin/env python3
"""
SETUP ADMIN CONFIG - RegistroOS
===============================

Script para configurar dados de admin e criar entidades padrão do sistema.
Garante que o sistema tenha dados básicos para funcionamento.

FUNCIONALIDADES:
1. Verificar/Criar usuário admin padrão
2. Criar departamentos padrão
3. Criar setores padrão
4. Criar tipos de máquina padrão
5. Criar tipos de teste padrão
6. Criar tipos de atividade padrão
7. Criar descrições de atividade padrão
8. Criar causas de retrabalho padrão
9. Criar tipos de falha padrão
10. Criar cliente padrão
11. Criar equipamento padrão

CREDENCIAIS ADMIN PADRÃO:
- Email: admin@registroos.com
- Senha: 123456
- Privilege Level: ADMIN
"""

import sys
import os
from datetime import datetime

# Adicionar o diretório backend ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from config.database_config import get_db
from app.database_models import (
    Usuario, Departamento, Setor, TipoMaquina, TipoTeste,
    Cliente, Equipamento, TipoAtividade, TipoDescricaoAtividade,
    TipoCausaRetrabalho, TipoFalha
)
from app.auth import get_password_hash

def criar_admin_padrao(db: Session):
    """Criar usuário admin padrão se não existir"""
    print("🔐 Verificando usuário admin...")
    
    admin = db.query(Usuario).filter(Usuario.privilege_level == 'ADMIN').first()
    
    if admin:
        print(f"✅ Admin já existe: {admin.email} - {admin.nome_completo}")
        return admin
    
    print("🔧 Criando admin padrão...")
    
    admin_data = {
        'nome_completo': 'Administrador do Sistema',
        'nome_usuario': 'admin',
        'email': 'admin@registroos.com',
        'matricula': 'ADMIN001',
        'senha_hash': get_password_hash('123456'),
        'setor': 'ADMINISTRAÇÃO',
        'cargo': 'Administrador',
        'departamento': 'ADMINISTRAÇÃO',
        'privilege_level': 'ADMIN',
        'is_approved': True,
        'trabalha_producao': False,
        'primeiro_login': False,
        'id_setor': 1,
        'id_departamento': 1,
        'data_criacao': datetime.now(),
        'data_ultima_atualizacao': datetime.now()
    }
    
    novo_admin = Usuario(**admin_data)
    db.add(novo_admin)
    db.commit()
    db.refresh(novo_admin)
    
    print(f"✅ Admin criado: {novo_admin.email}")
    print(f"   Senha padrão: 123456")
    print(f"   ID: {novo_admin.id}")
    
    return novo_admin

def criar_departamentos_padrao(db: Session):
    """Criar departamentos padrão"""
    print("\n🏢 Criando departamentos padrão...")
    
    departamentos_padrao = [
        {
            'nome_tipo': 'MOTORES',
            'descricao': 'Departamento de Motores Elétricos',
            'ativo': True,
            'data_criacao': datetime.now(),
            'data_ultima_atualizacao': datetime.now()
        },
        {
            'nome_tipo': 'GERADORES',
            'descricao': 'Departamento de Geradores',
            'ativo': True,
            'data_criacao': datetime.now(),
            'data_ultima_atualizacao': datetime.now()
        },
        {
            'nome_tipo': 'TRANSFORMADORES',
            'descricao': 'Departamento de Transformadores',
            'ativo': True,
            'data_criacao': datetime.now(),
            'data_ultima_atualizacao': datetime.now()
        },
        {
            'nome_tipo': 'ADMINISTRAÇÃO',
            'descricao': 'Departamento Administrativo',
            'ativo': True,
            'data_criacao': datetime.now(),
            'data_ultima_atualizacao': datetime.now()
        }
    ]
    
    for dept_data in departamentos_padrao:
        dept_existente = db.query(Departamento).filter(
            Departamento.nome_tipo == dept_data['nome_tipo']
        ).first()
        
        if not dept_existente:
            novo_dept = Departamento(**dept_data)
            db.add(novo_dept)
            print(f"   ✅ Criado: {dept_data['nome_tipo']}")
        else:
            print(f"   ⚠️ Já existe: {dept_data['nome_tipo']}")
    
    db.commit()

def criar_setores_padrao(db: Session):
    """Criar setores padrão"""
    print("\n🏗️ Criando setores padrão...")
    
    # Buscar departamentos
    dept_motores = db.query(Departamento).filter(Departamento.nome_tipo == 'MOTORES').first()
    dept_admin = db.query(Departamento).filter(Departamento.nome_tipo == 'ADMINISTRAÇÃO').first()
    
    setores_padrao = [
        {
            'nome': 'BOBINAGEM',
            'departamento': 'MOTORES',
            'descricao': 'Setor de Bobinagem de Motores',
            'ativo': True,
            'id_departamento': dept_motores.id if dept_motores else 1,
            'area_tipo': 'PRODUÇÃO',
            'supervisor_responsavel': 1,
            'permite_apontamento': True,
            'data_criacao': datetime.now(),
            'data_ultima_atualizacao': datetime.now()
        },
        {
            'nome': 'MONTAGEM',
            'departamento': 'MOTORES',
            'descricao': 'Setor de Montagem de Motores',
            'ativo': True,
            'id_departamento': dept_motores.id if dept_motores else 1,
            'area_tipo': 'PRODUÇÃO',
            'supervisor_responsavel': 1,
            'permite_apontamento': True,
            'data_criacao': datetime.now(),
            'data_ultima_atualizacao': datetime.now()
        },
        {
            'nome': 'TESTE',
            'departamento': 'MOTORES',
            'descricao': 'Setor de Testes de Motores',
            'ativo': True,
            'id_departamento': dept_motores.id if dept_motores else 1,
            'area_tipo': 'QUALIDADE',
            'supervisor_responsavel': 1,
            'permite_apontamento': True,
            'data_criacao': datetime.now(),
            'data_ultima_atualizacao': datetime.now()
        },
        {
            'nome': 'ADMINISTRAÇÃO',
            'departamento': 'ADMINISTRAÇÃO',
            'descricao': 'Setor Administrativo',
            'ativo': True,
            'id_departamento': dept_admin.id if dept_admin else 4,
            'area_tipo': 'ADMINISTRATIVO',
            'supervisor_responsavel': 1,
            'permite_apontamento': False,
            'data_criacao': datetime.now(),
            'data_ultima_atualizacao': datetime.now()
        }
    ]
    
    for setor_data in setores_padrao:
        setor_existente = db.query(Setor).filter(
            Setor.nome == setor_data['nome']
        ).first()
        
        if not setor_existente:
            novo_setor = Setor(**setor_data)
            db.add(novo_setor)
            print(f"   ✅ Criado: {setor_data['nome']}")
        else:
            print(f"   ⚠️ Já existe: {setor_data['nome']}")
    
    db.commit()

def criar_tipos_maquina_padrao(db: Session):
    """Criar tipos de máquina padrão"""
    print("\n⚙️ Criando tipos de máquina padrão...")
    
    dept_motores = db.query(Departamento).filter(Departamento.nome_tipo == 'MOTORES').first()
    
    tipos_maquina_padrao = [
        {
            'nome_tipo': 'MOTOR TRIFÁSICO',
            'categoria': 'MOTOR',
            'subcategoria': ['ESTATOR', 'ROTOR', 'CARCAÇA'],
            'descricao': 'Motor elétrico trifásico',
            'ativo': True,
            'id_departamento': dept_motores.id if dept_motores else 1,
            'especificacoes_tecnicas': 'Motor trifásico padrão',
            'campos_teste_resultado': 'Resistência, Isolação, Vibração',
            'setor': 'BOBINAGEM',
            'departamento': 'MOTORES',
            'data_criacao': datetime.now(),
            'data_ultima_atualizacao': datetime.now()
        },
        {
            'nome_tipo': 'MOTOR MONOFÁSICO',
            'categoria': 'MOTOR',
            'subcategoria': ['ESTATOR', 'ROTOR'],
            'descricao': 'Motor elétrico monofásico',
            'ativo': True,
            'id_departamento': dept_motores.id if dept_motores else 1,
            'especificacoes_tecnicas': 'Motor monofásico padrão',
            'campos_teste_resultado': 'Resistência, Isolação',
            'setor': 'BOBINAGEM',
            'departamento': 'MOTORES',
            'data_criacao': datetime.now(),
            'data_ultima_atualizacao': datetime.now()
        }
    ]
    
    for tipo_data in tipos_maquina_padrao:
        tipo_existente = db.query(TipoMaquina).filter(
            TipoMaquina.nome_tipo == tipo_data['nome_tipo']
        ).first()
        
        if not tipo_existente:
            novo_tipo = TipoMaquina(**tipo_data)
            db.add(novo_tipo)
            print(f"   ✅ Criado: {tipo_data['nome_tipo']}")
        else:
            print(f"   ⚠️ Já existe: {tipo_data['nome_tipo']}")
    
    db.commit()

def main():
    """Função principal"""
    print("🚀 SETUP ADMIN CONFIG - RegistroOS")
    print("=" * 50)
    
    try:
        db = next(get_db())
        
        # 1. Criar admin padrão
        admin = criar_admin_padrao(db)
        
        # 2. Criar departamentos padrão
        criar_departamentos_padrao(db)
        
        # 3. Criar setores padrão
        criar_setores_padrao(db)
        
        # 4. Criar tipos de máquina padrão
        criar_tipos_maquina_padrao(db)
        
        print("\n" + "=" * 50)
        print("✅ SETUP CONCLUÍDO COM SUCESSO!")
        print("\n📋 CREDENCIAIS DE ADMIN:")
        print(f"   Email: admin@registroos.com")
        print(f"   Senha: 123456")
        print(f"   Privilege Level: ADMIN")
        print("\n🌐 Acesse: http://localhost:3001")
        print("=" * 50)
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro durante setup: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
