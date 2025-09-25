"""
Database Models - RegistroOS - ESQUEMA CORRETO
===============================================
Modelos SQLAlchemy conforme esquema EXATO fornecido pelo usuário.
"""

import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Time, Boolean, Float, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from config.database_config import Base

# ========== TABELAS PRINCIPAIS ==========

class OrdemServico(Base):
    __tablename__ = "ordens_servico"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    os_numero = Column(String, nullable=False)
    status_os = Column(String)
    prioridade = Column(String, default='MEDIA')
    id_responsavel_registro = Column(Integer)
    id_responsavel_pcp = Column(Integer)
    id_responsavel_final = Column(Integer)
    data_inicio_prevista = Column(DateTime)
    data_fim_prevista = Column(DateTime)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    criado_por = Column(Integer)
    status_geral = Column(String)
    valor_total_previsto = Column(DECIMAL)
    valor_total_real = Column(DECIMAL)
    observacoes_gerais = Column(Text)
    id_tipo_maquina = Column(Integer)
    custo_total_real = Column(DECIMAL)
    horas_previstas = Column(DECIMAL)
    horas_reais = Column(DECIMAL)
    data_programacao = Column(DateTime)
    horas_orcadas = Column(DECIMAL(10,2), default=0)
    testes_iniciais_finalizados = Column(Boolean, default=0)
    testes_parciais_finalizados = Column(Boolean, default=0)
    testes_finais_finalizados = Column(Boolean, default=0)
    data_testes_iniciais_finalizados = Column(DateTime)
    data_testes_parciais_finalizados = Column(DateTime)
    data_testes_finais_finalizados = Column(DateTime)
    id_usuario_testes_iniciais = Column(Integer)
    id_usuario_testes_parciais = Column(Integer)
    id_usuario_testes_finais = Column(Integer)
    testes_exclusivo_os = Column(Text)
    # FKs CORRETOS:
    id_cliente = Column(Integer)
    id_equipamento = Column(Integer)
    id_setor = Column(Integer)
    id_departamento = Column(Integer)
    inicio_os = Column(DateTime)
    fim_os = Column(DateTime)
    descricao_maquina = Column(Text)

class ApontamentoDetalhado(Base):
    __tablename__ = "apontamentos_detalhados"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    id_os = Column(Integer, nullable=False)
    id_usuario = Column(Integer, nullable=False)
    id_setor = Column(Integer, nullable=False)
    data_hora_inicio = Column(DateTime, nullable=False)
    data_hora_fim = Column(DateTime)
    status_apontamento = Column(String, nullable=False)
    foi_retrabalho = Column(Boolean, default=0)
    causa_retrabalho = Column(String)
    observacao_os = Column(Text)
    servico_de_campo = Column(Boolean)
    observacoes_gerais = Column(Text)
    aprovado_supervisor = Column(Boolean)
    data_aprovacao_supervisor = Column(DateTime)
    supervisor_aprovacao = Column(String)
    criado_por = Column(String)
    criado_por_email = Column(String)
    data_processo_finalizado = Column(DateTime)
    setor = Column(String)
    horas_orcadas = Column(DECIMAL(10,2), default=0)
    etapa_inicial = Column(Boolean, default=0)
    etapa_parcial = Column(Boolean, default=0)
    etapa_final = Column(Boolean, default=0)
    horas_etapa_inicial = Column(DECIMAL, default=0)
    horas_etapa_parcial = Column(DECIMAL, default=0)
    horas_etapa_final = Column(DECIMAL, default=0)
    observacoes_etapa_inicial = Column(Text)
    observacoes_etapa_parcial = Column(Text)
    observacoes_etapa_final = Column(Text)
    data_etapa_inicial = Column(DateTime)
    data_etapa_parcial = Column(DateTime)
    data_etapa_final = Column(DateTime)
    supervisor_etapa_inicial = Column(String)
    supervisor_etapa_parcial = Column(String)
    supervisor_etapa_final = Column(String)
    tipo_maquina = Column(String)
    tipo_atividade = Column(String)
    descricao_atividade = Column(Text)
    categoria_maquina = Column(String)
    subcategorias_maquina = Column(Text)
    subcategorias_finalizadas = Column(Boolean, default=0)
    data_finalizacao_subcategorias = Column(DateTime)
    emprestimo_setor = Column(String)
    pendencia = Column(Boolean, default=0)
    pendencia_data = Column(DateTime)

class Pendencia(Base):
    __tablename__ = "pendencias"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    numero_os = Column(String, nullable=False)
    cliente = Column(String, nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    id_responsavel_inicio = Column(Integer, nullable=False)
    tipo_maquina = Column(String, nullable=False)
    descricao_maquina = Column(Text, nullable=False)
    descricao_pendencia = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    prioridade = Column(String)
    data_fechamento = Column(DateTime)
    id_responsavel_fechamento = Column(Integer)
    solucao_aplicada = Column(Text)
    observacoes_fechamento = Column(Text)
    id_apontamento_origem = Column(Integer)
    id_apontamento_fechamento = Column(Integer)
    tempo_aberto_horas = Column(Float)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)

class Programacao(Base):
    __tablename__ = "programacoes"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    id_ordem_servico = Column(Integer)
    criado_por_id = Column(Integer, nullable=False)
    responsavel_id = Column(Integer)
    observacoes = Column(Text)
    status = Column(String)
    inicio_previsto = Column(DateTime, nullable=False)
    fim_previsto = Column(DateTime, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    id_setor = Column(Integer)

class ResultadoTeste(Base):
    __tablename__ = "resultados_teste"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    id_apontamento = Column(Integer, nullable=False)
    id_teste = Column(Integer, nullable=False)
    resultado = Column(String, nullable=False)
    observacao = Column(Text)
    data_registro = Column(DateTime)

class OSTestesExclusivosFinalizados(Base):
    __tablename__ = "os_testes_exclusivos_finalizados"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    numero_os = Column(String, nullable=False)
    id_teste_exclusivo = Column(Integer, nullable=False)
    nome_teste = Column(String, nullable=False)
    descricao_teste = Column(String)
    usuario_finalizacao = Column(String, nullable=False)
    departamento = Column(String, nullable=False)
    setor = Column(String, nullable=False)
    data_finalizacao = Column(Date, nullable=False)
    hora_finalizacao = Column(Time, nullable=False)
    descricao_atividade = Column(Text)
    observacoes = Column(Text)
    data_criacao = Column(DateTime)

# ========== TABELAS REFERENCIAIS ==========

class Cliente(Base):
    __tablename__ = "clientes"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    razao_social = Column(String, nullable=False)
    nome_fantasia = Column(String)
    cnpj_cpf = Column(String)
    contato_principal = Column(String)
    telefone_contato = Column(String)
    email_contato = Column(String)
    endereco = Column(Text)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)

class Equipamento(Base):
    __tablename__ = "equipamentos"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    descricao = Column(Text, nullable=False)
    tipo = Column(String)
    fabricante = Column(String)
    modelo = Column(String)
    numero_serie = Column(String)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)

class Usuario(Base):
    __tablename__ = "tipo_usuarios"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    nome_completo = Column(String, nullable=False)
    nome_usuario = Column(String, nullable=False)
    email = Column(String, nullable=False)
    matricula = Column(String)
    senha_hash = Column(String, nullable=False)
    setor = Column(String, nullable=False)
    cargo = Column(String)
    departamento = Column(String, nullable=False)
    privilege_level = Column(String, nullable=False)
    is_approved = Column(Boolean, nullable=False)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    trabalha_producao = Column(Boolean, nullable=False)
    obs_reprovacao = Column(Text)
    id_setor = Column(Integer)
    id_departamento = Column(Integer)
    primeiro_login = Column(Boolean, nullable=False)

class Setor(Base):
    __tablename__ = "tipo_setores"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    departamento = Column(String, nullable=False)
    descricao = Column(Text)
    ativo = Column(Boolean)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    id_departamento = Column(Integer)
    area_tipo = Column(String, nullable=False)
    supervisor_responsavel = Column(Integer)
    permite_apontamento = Column(Boolean)

class Departamento(Base):
    __tablename__ = "tipo_departamentos"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    nome_tipo = Column(String)
    descricao = Column(Text)
    ativo = Column(Boolean)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)

class TipoMaquina(Base):
    __tablename__ = "tipos_maquina"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    nome_tipo = Column(String, nullable=False)
    categoria = Column(String)
    descricao = Column(Text)
    ativo = Column(Boolean)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    id_departamento = Column(Integer)
    especificacoes_tecnicas = Column(Text)
    campos_teste_resultado = Column(Text)
    setor = Column(String)
    departamento = Column(Text)

class TipoAtividade(Base):
    __tablename__ = "tipo_atividade"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    nome_tipo = Column(String, nullable=False)
    descricao = Column(Text)
    categoria = Column(String)
    ativo = Column(Boolean)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    id_tipo_maquina = Column(Integer)

class TipoDescricaoAtividade(Base):
    __tablename__ = "tipo_descricao_atividade"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String, nullable=False)
    descricao = Column(Text, nullable=False)
    categoria = Column(String)
    ativo = Column(Boolean)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    setor = Column(String)

class TipoCausaRetrabalho(Base):
    __tablename__ = "tipo_causas_retrabalho"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    ativo = Column(Boolean)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    id_departamento = Column(Integer)
    departamento = Column(Text)
    setor = Column(Text)

class TipoTeste(Base):
    __tablename__ = "tipos_teste"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    departamento = Column(String, nullable=False)
    setor = Column(String)
    tipo_teste = Column(String)
    descricao = Column(Text)
    ativo = Column(Boolean)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    tipo_maquina = Column(String)
    teste_exclusivo_setor = Column(Boolean)
    descricao_teste_exclusivo = Column(String)
    categoria = Column(String)
    subcategoria = Column(Integer)

# ========== TABELAS SISTEMA ==========

class MigrationLog(Base):
    __tablename__ = "migration_log"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    fase = Column(Text, nullable=False)
    acao = Column(Text, nullable=False)
    tabela_afetada = Column(Text)
    registros_afetados = Column(Integer)
    data_execucao = Column(DateTime)
    observacoes = Column(Text)

# Aliases para compatibilidade
TipoUsuario = Usuario
