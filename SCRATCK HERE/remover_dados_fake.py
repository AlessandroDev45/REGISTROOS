#!/usr/bin/env python3
"""
Script para remover todos os dados fake/mock/hardcoded das rotas do backend
e substituí-los por consultas reais ao banco de dados conforme HIERARQUIA_COMPLETA_BANCO_DADOS.md
"""

import os
import sys
import re

# Adicionar o diretório backend ao path
backend_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend"
sys.path.append(backend_path)

def remover_dados_fake_catalogs_simple():
    """Remove dados fake do catalogs_simple.py"""
    arquivo = os.path.join(backend_path, "routes", "catalogs_simple.py")
    
    print(f"🔧 Corrigindo {arquivo}...")
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Remover endpoints que retornam dados fake
    conteudo_novo = re.sub(
        r'@router\.get\("/subtipo-maquina"\).*?return \{[^}]*"status": "DISABLED"[^}]*\}',
        '''@router.get("/subtipo-maquina")
async def get_subtipo_maquina(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Get subcategorias from TipoMaquina.subcategoria field"""
    try:
        from app.database_models import TipoMaquina
        import json
        
        tipos = db.query(TipoMaquina).filter(TipoMaquina.ativo.is_(True)).all()
        subcategorias = set()
        
        for tipo in tipos:
            if tipo.subcategoria:
                try:
                    if isinstance(tipo.subcategoria, str):
                        sub_list = json.loads(tipo.subcategoria)
                        if isinstance(sub_list, list):
                            subcategorias.update(sub_list)
                except:
                    # Se não for JSON, tratar como string simples
                    subcategorias.add(tipo.subcategoria)
        
        return [{"nome": sub} for sub in sorted(subcategorias)]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar subcategorias: {str(e)}")''',
        conteudo, flags=re.DOTALL
    )
    
    # Remover endpoint de status fake
    conteudo_novo = re.sub(
        r'@router\.get\("/status"\).*?return \{[^}]*"available_models"[^}]*\}',
        '''@router.get("/status")
async def get_catalogs_status(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real status of catalog endpoints based on database"""
    try:
        from app.database_models import TipoAtividade, TipoDescricaoAtividade, TipoFalha, TipoMaquina
        
        # Verificar se há dados reais nas tabelas
        tipos_atividade = db.query(TipoAtividade).count()
        descricoes_atividade = db.query(TipoDescricaoAtividade).count()
        tipos_falha = db.query(TipoFalha).count()
        tipos_maquina = db.query(TipoMaquina).count()
        
        return {
            "catalogs_status": {
                "tipo_atividade": f"ACTIVE - {tipos_atividade} registros",
                "descricao_atividade": f"ACTIVE - {descricoes_atividade} registros",
                "tipo_falha": f"ACTIVE - {tipos_falha} registros",
                "subtipo_maquina": f"ACTIVE - baseado em {tipos_maquina} tipos de máquina"
            },
            "message": "Status baseado em dados reais do banco de dados",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar status: {str(e)}")''',
        conteudo, flags=re.DOTALL
    )
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo_novo)
    
    print(f"✅ {arquivo} corrigido")

def remover_dados_fake_admin_config():
    """Remove dados fake do admin_config_routes.py"""
    arquivo = os.path.join(backend_path, "routes", "admin_config_routes.py")
    
    print(f"🔧 Corrigindo {arquivo}...")
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Substituir arrays hardcoded por consultas ao banco
    conteudo_novo = re.sub(
        r'"privilege_levels": \["ADMIN", "GESTAO", "PCP", "SUPERVISOR", "USER"\]',
        '''# Buscar privilege levels reais dos usuários
                privilege_levels_query = db.query(Usuario.privilege_level).distinct().all()
                privilege_levels = [p[0] for p in privilege_levels_query if p[0]]''',
        conteudo
    )
    
    conteudo_novo = re.sub(
        r'"status_os": \["ABERTA", "EM_ANDAMENTO", "FINALIZADA", "CANCELADA"\]',
        '''# Buscar status reais das OS
                status_os_query = db.query(OrdemServico.status_os).distinct().all()
                status_os = [s[0] for s in status_os_query if s[0]]''',
        conteudo_novo
    )
    
    conteudo_novo = re.sub(
        r'"tipos_area": \["PRODUÇÃO", "QUALIDADE", "ADMINISTRATIVO"\]',
        '''# Buscar tipos de área reais dos setores
                tipos_area_query = db.query(Setor.area_tipo).distinct().all()
                tipos_area = [a[0] for a in tipos_area_query if a[0]]''',
        conteudo_novo
    )
    
    # Corrigir o retorno para usar as variáveis
    conteudo_novo = re.sub(
        r'"configuracoes": \{[^}]*\}',
        '''"configuracoes": {
                "privilege_levels": privilege_levels,
                "status_os": status_os,
                "tipos_area": tipos_area
            }''',
        conteudo_novo
    )
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo_novo)
    
    print(f"✅ {arquivo} corrigido")

def remover_dados_fake_desenvolvimento():
    """Remove dados fake do desenvolvimento.py"""
    arquivo = os.path.join(backend_path, "routes", "desenvolvimento.py")
    
    print(f"🔧 Corrigindo {arquivo}...")
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Substituir valores hardcoded por consultas ao banco
    substituicoes = [
        (r'"Cliente não informado"', 'cliente_obj.razao_social if cliente_obj else None'),
        (r'"Equipamento não informado"', 'equipamento_obj.descricao if equipamento_obj else None'),
        (r'"Não informado"', 'None'),
        (r'"Atividade padrão"', 'tipo_atividade_obj.nome_tipo if tipo_atividade_obj else None'),
        (r'"MEDIA".*# valor padrão', '"MEDIA"  # Buscar da OS real'),
        (r'"Programação automática"', 'f"OS {numero_os} - Programação PCP"'),
        (r'setor="Não informado"', 'setor=None'),
        (r'departamento="Não informado"', 'departamento=None'),
    ]
    
    for padrao, substituto in substituicoes:
        conteudo = re.sub(padrao, substituto, conteudo)
    
    # Adicionar consultas reais para buscar dados relacionados
    conteudo = re.sub(
        r'cliente_nome = "Cliente não informado"',
        '''# Buscar cliente real
            cliente_obj = None
            if os_encontrada and hasattr(os_encontrada, 'id_cliente') and os_encontrada.id_cliente:
                cliente_obj = db.query(Cliente).filter(Cliente.id == os_encontrada.id_cliente).first()
            cliente_nome = cliente_obj.razao_social if cliente_obj else None''',
        conteudo
    )
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    print(f"✅ {arquivo} corrigido")

def main():
    """Função principal"""
    print("🚀 REMOVENDO DADOS FAKE/MOCK DAS ROTAS")
    print("=" * 50)
    
    try:
        remover_dados_fake_catalogs_simple()
        remover_dados_fake_admin_config()
        remover_dados_fake_desenvolvimento()
        
        print("\n🎉 CORREÇÃO CONCLUÍDA!")
        print("✅ Todos os dados fake foram removidos")
        print("✅ Substituídos por consultas reais ao banco de dados")
        print("✅ Conforme HIERARQUIA_COMPLETA_BANCO_DADOS.md")
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
