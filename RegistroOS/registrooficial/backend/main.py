from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from config.database_config import engine, get_db
from app.database_models import Base, Usuario, ApontamentoDetalhado, OrdemServico, Cliente, Equipamento
from routes.auth import get_current_user

# Criar aplicação FastAPI
app = FastAPI(
    title="RegistroOS API",
    description="API para sistema de registro de ordens de serviço",
    version="1.9.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar tabelas no banco de dados (COMENTADO - tabelas já existem)
# Base.metadata.create_all(bind=engine)

# Importar e incluir rotas
try:
    import sys
    import os
    # Adiciona o diretório 'backend' ao sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)

    # Importar os routers dos arquivos de rota
    from routes.auth import router as auth_router
    from routes.os_routes_simple import router as os_router
    from routes.catalogs_validated import router as catalogs_router
    from routes.desenvolvimento import router as desenvolvimento_router
    from routes.users import router as users_router
    from routes.admin_routes_simple import router as admin_router
    from routes.admin_config_routes import router as admin_config_router
    from routes.pcp_routes import router as pcp_router
    from routes.gestao_routes import router as gestao_router
    from routes.relatorio_completo import router as relatorio_router
    from routes.general import router as general_router

    # Incluir os routers na aplicação FastAPI
    app.include_router(auth_router, prefix="/api", tags=["auth"])
    app.include_router(desenvolvimento_router, prefix="/api/desenvolvimento", tags=["desenvolvimento"])
    app.include_router(os_router, prefix="/api", tags=["os"])
    app.include_router(catalogs_router, prefix="/api", tags=["catalogs"])
    app.include_router(users_router, prefix="/api/users", tags=["users"])
    app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
    app.include_router(admin_config_router, prefix="/api/admin/config", tags=["admin-config"])

    app.include_router(pcp_router, prefix="/api/pcp", tags=["pcp"])
    app.include_router(gestao_router, prefix="/api/gestao", tags=["gestao"])
    app.include_router(relatorio_router, tags=["relatorio-completo"])
    app.include_router(general_router, prefix="/api", tags=["general"])

    print("✅ Todas as rotas carregadas com sucesso")
    
except ImportError as e:
    print(f"❌ Erro ao importar rotas: {e}")
    print(f"Detalhes do erro: {e.__class__.__name__}: {e}")
    import traceback
    traceback.print_exc()

@app.get("/")
async def root():
    return {"message": "RegistroOS API está funcionando!", "version": "1.9.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "RegistroOS API"}

# Endpoints globais simplificados para compatibilidade
@app.get("/api/ordens-servico")
async def get_ordens_servico_global():
    """Endpoint global simplificado"""
    return [
        {
            "id": 1,
            "os_numero": "15225",
            "descricao_maquina": "MOTOR DE INDUCAO",
            "status": "EM ANDAMENTO",
            "data_abertura": "2025-09-01T00:00:00",
            "data_fechamento": None,
            "id_cliente": 1,
            "id_tipo_maquina": 1,
            "teste_daimer": False,
            "teste_carga": False,
            "cliente_nome": "Cliente Teste",
            "tipo_maquina_nome": "Motor"
        }
    ]

@app.get("/api/programacoes")
async def get_programacoes_global():
    """Endpoint global simplificado"""
    return [
        {
            "id": 1,
            "id_ordem_servico": 1,
            "responsavel_id": 1,
            "inicio_previsto": "2025-09-18T08:00:00",
            "fim_previsto": "2025-09-18T17:00:00",
            "status": "PROGRAMADA",
            "criado_por_id": 1,
            "observacoes": "Programação teste",
            "created_at": "2025-09-18T06:00:00",
            "updated_at": "2025-09-18T06:00:00",
            "id_setor": 1,
            "os_numero": "15225",
            "responsavel_nome": "ADMINISTRADOR"
        }
    ]

@app.get("/api/apontamentos-detalhados")
async def get_apontamentos_detalhados_global(
    setor: Optional[str] = Query(None),
    departamento: Optional[str] = Query(None),
    usuario_id: Optional[int] = Query(None),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    nome_tecnico: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ENDPOINT GLOBAL: Apontamentos detalhados para Dashboard e Gerenciar Registros
    Aceita parâmetros de query para filtragem avançada
    """
    try:
        print(f"🔍 Buscando apontamentos detalhados para usuário: {current_user.nome_completo} ({current_user.privilege_level})")
        print(f"📋 Parâmetros recebidos: setor={setor}, departamento={departamento}, usuario_id={usuario_id}, data_inicio={data_inicio}, data_fim={data_fim}, nome_tecnico={nome_tecnico}")

        # Buscar apontamentos detalhados do banco de dados
        query = db.query(ApontamentoDetalhado)

        # Aplicar filtros baseados no privilégio do usuário
        try:
            privilege_level = getattr(current_user, 'privilege_level', 'USER')

            # Aplicar filtros de parâmetros de query primeiro
            if usuario_id:
                query = query.filter(ApontamentoDetalhado.id_usuario == usuario_id)
            elif privilege_level == 'USER':
                # Usuários normais só veem seus próprios apontamentos
                query = query.filter(ApontamentoDetalhado.id_usuario == current_user.id)
            elif privilege_level == 'SUPERVISOR':
                # Supervisores veem apontamentos do seu setor
                if setor:
                    # Se setor foi especificado nos parâmetros, usar ele
                    user_setor_id = getattr(current_user, 'id_setor', None)
                    if user_setor_id:
                        query = query.filter(ApontamentoDetalhado.id_setor == user_setor_id)
                else:
                    # Usar setor do supervisor
                    user_setor_id = getattr(current_user, 'id_setor', None)
                    if user_setor_id:
                        query = query.filter(ApontamentoDetalhado.id_setor == user_setor_id)
            # ADMIN e GESTAO veem todos os apontamentos (sem filtro adicional)

            # Aplicar filtros de data se especificados
            if data_inicio:
                from datetime import datetime
                try:
                    data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                    query = query.filter(func.date(ApontamentoDetalhado.data_hora_inicio) >= data_inicio_dt)
                except ValueError:
                    pass

            if data_fim:
                from datetime import datetime
                try:
                    data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d').date()
                    query = query.filter(func.date(ApontamentoDetalhado.data_hora_inicio) <= data_fim_dt)
                except ValueError:
                    pass

        except Exception as e:
            print(f"⚠️ Erro ao aplicar filtros de usuário: {e}")
            # Em caso de erro, mostrar apenas apontamentos do usuário atual
            query = query.filter(ApontamentoDetalhado.id_usuario == current_user.id)

        # Limitar a 50 registros mais recentes
        apontamentos = query.order_by(ApontamentoDetalhado.data_hora_inicio.desc()).limit(50).all()
        print(f"📊 Encontrados {len(apontamentos)} apontamentos")

        # Converter para formato de resposta
        result = []
        for apt in apontamentos:
            try:
                # Buscar OS manualmente
                os = db.query(OrdemServico).filter(OrdemServico.id == apt.id_os).first()
                numero_os = os.os_numero if os else "N/A"

                # Buscar cliente através da relação
                cliente_nome = "N/A"
                try:
                    if os and hasattr(os, 'id_cliente'):
                        id_cliente = getattr(os, 'id_cliente', None)
                        if id_cliente:
                            cliente = db.query(Cliente).filter(Cliente.id == id_cliente).first()
                            if cliente:
                                cliente_nome = cliente.razao_social or cliente.nome_fantasia or "Cliente não informado"
                except Exception as e:
                    cliente_nome = "N/A"

                # Buscar equipamento através da relação
                equipamento_descricao = "N/A"
                try:
                    if os and hasattr(os, 'id_equipamento'):
                        id_equipamento = getattr(os, 'id_equipamento', None)
                        if id_equipamento:
                            equipamento = db.query(Equipamento).filter(Equipamento.id == id_equipamento).first()
                            if equipamento:
                                equipamento_descricao = equipamento.descricao or "Equipamento não informado"
                except Exception as e:
                    equipamento_descricao = "N/A"

                # Buscar dados diretamente do apontamento
                tipo_maquina_nome = getattr(apt, 'tipo_maquina', None) or "N/A"
                categoria_maquina = getattr(apt, 'categoria_maquina', None) or "N/A"
                subcategorias_maquina = getattr(apt, 'subcategorias_maquina', None) or "N/A"

                # Buscar descrição da máquina da OS
                descricao_maquina = "N/A"
                try:
                    if os and hasattr(os, 'descricao_maquina'):
                        descricao_maquina = getattr(os, 'descricao_maquina', None) or "N/A"
                except Exception as e:
                    descricao_maquina = "N/A"

                # Buscar usuário e departamento
                usuario = db.query(Usuario).filter(Usuario.id == apt.id_usuario).first()
                nome_usuario = usuario.nome_completo if usuario else "N/A"
                departamento_usuario = usuario.departamento if usuario else "N/A"

                # Converter datas de forma segura
                data_inicio = None
                data_fim = None
                hora_inicio = None
                hora_fim = None

                try:
                    if apt.data_hora_inicio is not None:
                        data_inicio = str(apt.data_hora_inicio)
                        hora_inicio = apt.data_hora_inicio.strftime("%H:%M")
                except:
                    data_inicio = None
                    hora_inicio = None

                try:
                    if apt.data_hora_fim is not None:
                        data_fim = str(apt.data_hora_fim)
                        hora_fim = apt.data_hora_fim.strftime("%H:%M")
                        print(f"🕐 Apontamento {apt.id}: data_hora_fim = {apt.data_hora_fim}, hora_fim = {hora_fim}")
                    else:
                        data_fim = None
                        hora_fim = None
                        print(f"🕐 Apontamento {apt.id}: data_hora_fim é NULL")
                except Exception as e:
                    print(f"⚠️ Erro ao converter data_hora_fim para apontamento {apt.id}: {e}")
                    data_fim = None
                    hora_fim = None

                # Calcular tempo trabalhado se houver data de início e fim
                tempo_trabalhado = 0.0
                try:
                    if apt.data_hora_inicio is not None and apt.data_hora_fim is not None:
                        delta = apt.data_hora_fim - apt.data_hora_inicio
                        tempo_trabalhado = delta.total_seconds() / 3600  # Converter para horas
                except:
                    tempo_trabalhado = 0.0

                # Obter tipo_atividade e descricao_atividade de forma segura
                tipo_atividade_str = "N/A"
                descricao_atividade_str = "N/A"
                try:
                    tipo_atividade_value = getattr(apt, 'tipo_atividade', None)
                    if tipo_atividade_value is not None:
                        tipo_atividade_str = str(tipo_atividade_value)

                    descricao_atividade_value = getattr(apt, 'descricao_atividade', None)
                    if descricao_atividade_value is not None:
                        descricao_atividade_str = str(descricao_atividade_value)
                except Exception as e:
                    tipo_atividade_str = "N/A"
                    descricao_atividade_str = "N/A"

                result.append({
                    "id": apt.id,
                    "numero_os": numero_os,
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                    "hora_inicio": hora_inicio,
                    "hora_fim": hora_fim,
                    "data_hora_inicio": data_inicio,  # Alias para compatibilidade
                    "status": getattr(apt, 'status_apontamento', 'N/A') or "N/A",
                    "observacoes": getattr(apt, 'observacao_os', '') or "",
                    "setor": getattr(apt, 'setor', 'N/A') or "N/A",
                    "departamento": departamento_usuario,
                    "foi_retrabalho": getattr(apt, 'foi_retrabalho', False) or False,
                    "usuario": nome_usuario,
                    "nome_tecnico": nome_usuario,  # Alias para compatibilidade
                    "tipo_atividade": tipo_atividade_str,
                    "descricao_atividade": descricao_atividade_str,
                    "tempo_trabalhado": tempo_trabalhado,
                    "aprovado_supervisor": bool(getattr(apt, 'aprovado_supervisor', False)),
                    "cliente": cliente_nome,
                    # Novos campos da OS
                    "equipamento": equipamento_descricao,
                    "tipo_maquina": tipo_maquina_nome,
                    "categoria_maquina": categoria_maquina,
                    "subcategorias_maquina": subcategorias_maquina,
                    "descricao_maquina": descricao_maquina
                })

            except Exception as e:
                print(f"⚠️ Erro ao processar apontamento {apt.id}: {e}")
                continue

        return result

    except Exception as e:
        print(f"❌ Erro ao buscar apontamentos detalhados: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar apontamentos: {str(e)}")

# ENDPOINT REMOVIDO - CONFLITAVA COM /api/pcp/programacao-form-data
# O endpoint correto está em routes/pcp_routes.py

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Iniciando RegistroOS Backend...")
    print("📍 Backend: http://localhost:8000")
    print("📋 Docs: http://localhost:8000/docs")
    print("🛑 Para parar: Ctrl+C")
    print("=" * 40)
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0", 
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido")
    finally:
        print("👋 Backend encerrado")
