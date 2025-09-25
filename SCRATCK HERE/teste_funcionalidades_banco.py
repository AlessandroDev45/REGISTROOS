#!/usr/bin/env python3
"""
TESTE COMPLETO DAS FUNCIONALIDADES DO BANCO
==========================================

Testa todas as funcionalidades que usam o banco de dados
após a limpeza dos campos duplicados.
"""

import sys
import os
sys.path.append('C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend')

from sqlalchemy.orm import Session
from config.database_config import get_db
from app.database_models import (
    OrdemServico, ApontamentoDetalhado, Usuario, Setor, Departamento,
    Cliente, Equipamento, TipoMaquina, Pendencia, Programacao, ResultadoTeste
)

def teste_modelos_basicos():
    """Teste básico dos modelos"""
    print("🧪 TESTANDO MODELOS BÁSICOS...")
    
    db = next(get_db())
    try:
        # Teste 1: Contar registros
        total_os = db.query(OrdemServico).count()
        total_apontamentos = db.query(ApontamentoDetalhado).count()
        total_usuarios = db.query(Usuario).count()
        
        print(f"  ✅ Ordens de Serviço: {total_os}")
        print(f"  ✅ Apontamentos: {total_apontamentos}")
        print(f"  ✅ Usuários: {total_usuarios}")
        
        # Teste 2: Buscar primeiro registro de cada tabela
        primeira_os = db.query(OrdemServico).first()
        primeiro_apontamento = db.query(ApontamentoDetalhado).first()
        primeiro_usuario = db.query(Usuario).first()
        
        print(f"  ✅ Primeira OS: {primeira_os.os_numero if primeira_os else 'Nenhuma'}")
        print(f"  ✅ Primeiro apontamento ID: {primeiro_apontamento.id if primeiro_apontamento else 'Nenhum'}")
        print(f"  ✅ Primeiro usuário: {primeiro_usuario.nome_completo if primeiro_usuario else 'Nenhum'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro nos modelos básicos: {str(e)}")
        return False
    finally:
        db.close()

def teste_relacionamentos():
    """Teste dos relacionamentos entre tabelas"""
    print("\n🔗 TESTANDO RELACIONAMENTOS...")
    
    db = next(get_db())
    try:
        # Teste 1: OS com Cliente
        os_com_cliente = db.query(OrdemServico).join(Cliente).first()
        if os_com_cliente:
            print(f"  ✅ OS {os_com_cliente.os_numero} → Cliente OK")
        else:
            print("  ⚠️ Nenhuma OS com cliente encontrada")
        
        # Teste 2: Apontamento com OS
        apontamento_com_os = db.query(ApontamentoDetalhado).join(OrdemServico).first()
        if apontamento_com_os:
            print(f"  ✅ Apontamento {apontamento_com_os.id} → OS OK")
        else:
            print("  ⚠️ Nenhum apontamento com OS encontrado")
        
        # Teste 3: Apontamento com Usuário
        apontamento_com_usuario = db.query(ApontamentoDetalhado).join(Usuario).first()
        if apontamento_com_usuario:
            print(f"  ✅ Apontamento {apontamento_com_usuario.id} → Usuário OK")
        else:
            print("  ⚠️ Nenhum apontamento com usuário encontrado")
        
        # Teste 4: Apontamento com Setor (usando id_setor)
        apontamento_com_setor = db.query(ApontamentoDetalhado).join(Setor, ApontamentoDetalhado.id_setor == Setor.id).first()
        if apontamento_com_setor:
            print(f"  ✅ Apontamento {apontamento_com_setor.id} → Setor OK")
        else:
            print("  ⚠️ Nenhum apontamento com setor encontrado")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro nos relacionamentos: {str(e)}")
        return False
    finally:
        db.close()

def teste_campos_removidos():
    """Teste para verificar se campos removidos não causam erros"""
    print("\n🗑️ TESTANDO CAMPOS REMOVIDOS...")
    
    db = next(get_db())
    try:
        # Teste 1: Verificar se status_geral foi removido de ordens_servico
        try:
            os = db.query(OrdemServico).first()
            # Tentar acessar campo removido deve dar erro
            _ = os.status_geral
            print("  ❌ Campo status_geral ainda existe!")
            return False
        except AttributeError:
            print("  ✅ Campo status_geral removido corretamente")
        
        # Teste 2: Verificar se setor foi removido de apontamentos_detalhados
        try:
            apontamento = db.query(ApontamentoDetalhado).first()
            # Tentar acessar campo removido deve dar erro
            _ = apontamento.setor
            print("  ❌ Campo setor ainda existe em apontamentos!")
            return False
        except AttributeError:
            print("  ✅ Campo setor removido corretamente de apontamentos")
        
        # Teste 3: Verificar se campos foram removidos de tipo_usuarios
        try:
            usuario = db.query(Usuario).first()
            # Tentar acessar campos removidos deve dar erro
            _ = usuario.setor
            print("  ❌ Campo setor ainda existe em usuarios!")
            return False
        except AttributeError:
            print("  ✅ Campo setor removido corretamente de usuarios")
        
        try:
            _ = usuario.departamento
            print("  ❌ Campo departamento ainda existe em usuarios!")
            return False
        except AttributeError:
            print("  ✅ Campo departamento removido corretamente de usuarios")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao testar campos removidos: {str(e)}")
        return False
    finally:
        db.close()

def teste_queries_complexas():
    """Teste de queries mais complexas"""
    print("\n🔍 TESTANDO QUERIES COMPLEXAS...")
    
    db = next(get_db())
    try:
        # Query 1: OS com dados relacionados
        query_os = db.query(
            OrdemServico.os_numero,
            OrdemServico.status_os,
            Cliente.razao_social,
            TipoMaquina.nome_tipo
        ).outerjoin(Cliente).outerjoin(TipoMaquina).limit(3)
        
        resultados_os = query_os.all()
        print(f"  ✅ Query OS complexa: {len(resultados_os)} resultados")
        
        # Query 2: Apontamentos com relacionamentos
        query_apontamentos = db.query(
            ApontamentoDetalhado.id,
            ApontamentoDetalhado.status_apontamento,
            OrdemServico.os_numero,
            Usuario.nome_completo,
            Setor.nome
        ).join(OrdemServico).join(Usuario).join(Setor, ApontamentoDetalhado.id_setor == Setor.id).limit(3)
        
        resultados_apontamentos = query_apontamentos.all()
        print(f"  ✅ Query Apontamentos complexa: {len(resultados_apontamentos)} resultados")
        
        # Query 3: Usuários com setores e departamentos
        query_usuarios = db.query(
            Usuario.nome_completo,
            Setor.nome.label('setor_nome'),
            Departamento.nome_tipo.label('departamento_nome')
        ).outerjoin(Setor, Usuario.id_setor == Setor.id).outerjoin(Departamento, Usuario.id_departamento == Departamento.id).limit(3)
        
        resultados_usuarios = query_usuarios.all()
        print(f"  ✅ Query Usuários complexa: {len(resultados_usuarios)} resultados")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro nas queries complexas: {str(e)}")
        return False
    finally:
        db.close()

def teste_novos_campos():
    """Teste dos novos campos adicionados"""
    print("\n🆕 TESTANDO NOVOS CAMPOS...")
    
    db = next(get_db())
    try:
        # Teste dos novos campos em apontamentos_detalhados
        apontamento = db.query(ApontamentoDetalhado).first()
        if apontamento:
            # Verificar se novos campos existem
            emprestimo = apontamento.emprestimo_setor
            pendencia = apontamento.pendencia
            pendencia_data = apontamento.pendencia_data
            
            print(f"  ✅ emprestimo_setor: {emprestimo}")
            print(f"  ✅ pendencia: {pendencia}")
            print(f"  ✅ pendencia_data: {pendencia_data}")
        else:
            print("  ⚠️ Nenhum apontamento para testar novos campos")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao testar novos campos: {str(e)}")
        return False
    finally:
        db.close()

def main():
    """Função principal de teste"""
    print("🧪 INICIANDO TESTES COMPLETOS DO BANCO DE DADOS")
    print("=" * 60)
    
    testes = [
        teste_modelos_basicos,
        teste_relacionamentos,
        teste_campos_removidos,
        teste_queries_complexas,
        teste_novos_campos
    ]
    
    sucessos = 0
    total = len(testes)
    
    for teste in testes:
        try:
            if teste():
                sucessos += 1
        except Exception as e:
            print(f"❌ Erro no teste {teste.__name__}: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTADO FINAL: {sucessos}/{total} testes passaram")
    
    if sucessos == total:
        print("✅ TODOS OS TESTES PASSARAM - BANCO FUNCIONANDO PERFEITAMENTE!")
        return True
    else:
        print(f"⚠️ {total - sucessos} testes falharam - Verificar problemas")
        return False

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)
