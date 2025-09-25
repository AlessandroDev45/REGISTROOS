from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config.database_config import engine, get_db
from app.database_models import Base, Usuario, ApontamentoDetalhado, OrdemServico
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
    from routes.auth import router as auth_router
    from routes.os_routes_simple import router as os_router
    from routes.catalogs_validated import router as catalogs_router
    from routes.desenvolvimento import router as desenvolvimento_router
    from routes.users import router as users_router
    from app.admin_routes_simple import router as admin_router
    from app.admin_config_routes import router as admin_config_router

    from routes.pcp_routes import router as pcp_router
    from app.gestao_routes import router as gestao_router
    from routes.relatorio_completo import router as relatorio_router
    from routes.general import router as general_router

    app.include_router(auth_router, prefix="/api", tags=["auth"])
    app.include_router(desenvolvimento_router, prefix="/api", tags=["desenvolvimento"])
    app.include_router(os_router, prefix="/api", tags=["os"])
    app.include_router(catalogs_router, prefix="/api", tags=["catalogs"])
    app.include_router(users_router, prefix="/api", tags=["users"])
    app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
    app.include_router(admin_config_router, prefix="/api/admin/config", tags=["admin-config"])

    app.include_router(pcp_router, prefix="/api/pcp", tags=["pcp"])
    app.include_router(gestao_router, prefix="/api/gestao", tags=["gestao"])
    app.include_router(relatorio_router, tags=["relatorio-completo"])
    app.include_router(general_router, prefix="/api", tags=["general"])

    print("✅ Todas as rotas carregadas com sucesso")
    
except ImportError as e:
    print(f"❌ Erro ao importar rotas: {e}")

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
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ENDPOINT GLOBAL: Apontamentos detalhados para Dashboard
    Redireciona para o endpoint correto em desenvolvimento.py
    """
    try:
        # Buscar apontamentos detalhados do banco de dados
        query = db.query(ApontamentoDetalhado)

        # Aplicar filtros baseados no privilégio do usuário
        try:
            privilege_level = getattr(current_user, 'privilege_level', 'USER')
            if privilege_level == 'USER':
                query = query.filter(ApontamentoDetalhado.id_usuario == current_user.id)
            elif privilege_level == 'SUPERVISOR':
                # Supervisores veem apontamentos do seu setor
                user_setor = getattr(current_user, 'setor', None)
                if user_setor:
                    query = query.filter(ApontamentoDetalhado.setor == user_setor)
            # ADMIN vê todos os apontamentos
        except Exception as e:
            print(f"⚠️ Erro ao aplicar filtros de usuário: {e}")
            # Em caso de erro, mostrar apenas apontamentos do usuário atual
            query = query.filter(ApontamentoDetalhado.id_usuario == current_user.id)

        # Limitar a 50 registros mais recentes
        apontamentos = query.order_by(ApontamentoDetalhado.data_hora_inicio.desc()).limit(50).all()

        # Converter para formato de resposta
        result = []
        for apt in apontamentos:
            # Buscar OS manualmente
            os = db.query(OrdemServico).filter(OrdemServico.id == apt.id_os).first()
            numero_os = os.os_numero if os else "N/A"

            # Buscar usuário
            usuario = db.query(Usuario).filter(Usuario.id == apt.id_usuario).first()
            nome_usuario = usuario.nome_completo if usuario else "N/A"

            # Converter datas de forma segura
            data_inicio = None
            data_fim = None
            try:
                data_inicio = str(apt.data_hora_inicio) if apt.data_hora_inicio is not None else None
            except:
                data_inicio = None

            try:
                data_fim = str(apt.data_hora_fim) if apt.data_hora_fim is not None else None
            except:
                data_fim = None

            # Calcular tempo trabalhado se houver data de início e fim
            tempo_trabalhado = 0.0
            try:
                if apt.data_hora_inicio is not None and apt.data_hora_fim is not None:
                    delta = apt.data_hora_fim - apt.data_hora_inicio
                    tempo_trabalhado = delta.total_seconds() / 3600  # Converter para horas
            except:
                tempo_trabalhado = 0.0

            result.append({
                "id": apt.id,
                "numero_os": numero_os,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "data_hora_inicio": data_inicio,  # Alias para compatibilidade
                "status": apt.status_apontamento or "N/A",
                "observacoes": apt.observacao_os or "",
                "setor": apt.setor or "N/A",
                "departamento": "N/A",  # Campo não existe na tabela atual
                "foi_retrabalho": apt.foi_retrabalho or False,
                "usuario": nome_usuario,
                "nome_tecnico": nome_usuario,  # Alias para compatibilidade
                "tipo_atividade": apt.tipo_atividade or "N/A",
                "tempo_trabalhado": tempo_trabalhado,
                "aprovado_supervisor": bool(getattr(apt, 'aprovado_supervisor', False)),
                "cliente": "N/A"  # Campo não disponível nos dados atuais
            })

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
