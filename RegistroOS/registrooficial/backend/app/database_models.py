"""
Database Models - RegistroOS - ESQUEMA CORRETO
===============================================
Modelos SQLAlchemy conforme esquema EXATO fornecido pelo usuário.
"""

import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Time, Boolean, Float, DECIMAL, ForeignKey, JSON
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
    id_responsavel_registro = Column(Integer, ForeignKey("tipo_usuarios.id"))
    id_responsavel_pcp = Column(Integer, ForeignKey("tipo_usuarios.id"))
    id_responsavel_final = Column(Integer, ForeignKey("tipo_usuarios.id"))
    data_inicio_prevista = Column(DateTime)
    data_fim_prevista = Column(DateTime)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    criado_por = Column(Integer, ForeignKey("tipo_usuarios.id"))
    status_geral = Column(String)
    valor_total_previsto = Column(DECIMAL)
    valor_total_real = Column(DECIMAL)
    observacoes_gerais = Column(Text)
    id_tipo_maquina = Column(Integer, ForeignKey("tipos_maquina.id"))
    custo_total_real = Column(DECIMAL)
    horas_previstas = Column(DECIMAL)
    horas_reais = Column(DECIMAL)
    data_programacao = Column(DateTime)
    horas_orcadas = Column(Text, default='{}')
    testes_iniciais_finalizados = Column(Boolean, default=0)
    testes_parciais_finalizados = Column(Boolean, default=0)
    testes_finais_finalizados = Column(Boolean, default=0)
    data_testes_iniciais_finalizados = Column(DateTime)
    data_testes_parciais_finalizados = Column(DateTime)
    data_testes_finais_finalizados = Column(DateTime)
    id_usuario_testes_iniciais = Column(Integer, ForeignKey("tipo_usuarios.id"))
    id_usuario_testes_parciais = Column(Integer, ForeignKey("tipo_usuarios.id"))
    id_usuario_testes_finais = Column(Integer, ForeignKey("tipo_usuarios.id"))
    testes_exclusivo_os = Column(Text)
    # FKs CONFORME HIERARQUIA:
    id_cliente = Column(Integer, ForeignKey("clientes.id"))
    id_equipamento = Column(Integer, ForeignKey("equipamentos.id"))
    id_setor = Column(Integer, ForeignKey("tipo_setores.id"))
    id_departamento = Column(Integer, ForeignKey("tipo_departamentos.id"))
    inicio_os = Column(DateTime)
    fim_os = Column(DateTime)
    descricao_maquina = Column(Text)

    # Relacionamentos conforme hierarquia
    responsavel_registro = relationship("Usuario", foreign_keys=[id_responsavel_registro])
    responsavel_pcp = relationship("Usuario", foreign_keys=[id_responsavel_pcp])
    responsavel_final = relationship("Usuario", foreign_keys=[id_responsavel_final])
    criado_por_obj = relationship("Usuario", foreign_keys=[criado_por])
    usuario_testes_iniciais = relationship("Usuario", foreign_keys=[id_usuario_testes_iniciais])
    usuario_testes_parciais = relationship("Usuario", foreign_keys=[id_usuario_testes_parciais])
    usuario_testes_finais = relationship("Usuario", foreign_keys=[id_usuario_testes_finais])
    tipo_maquina_obj = relationship("TipoMaquina", foreign_keys=[id_tipo_maquina])
    cliente_obj = relationship("Cliente", foreign_keys=[id_cliente])
    equipamento_obj = relationship("Equipamento", foreign_keys=[id_equipamento])
    setor_obj = relationship("Setor", foreign_keys=[id_setor])
    departamento_obj = relationship("Departamento", foreign_keys=[id_departamento])

    # Relacionamentos reversos
    apontamentos = relationship("ApontamentoDetalhado", back_populates="ordem_servico")
    programacoes = relationship("Programacao", back_populates="ordem_servico")
    pendencias = relationship("Pendencia", back_populates="ordem_servico")

class ApontamentoDetalhado(Base):
    __tablename__ = "apontamentos_detalhados"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    id_os = Column(Integer, ForeignKey("ordens_servico.id"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("tipo_usuarios.id"), nullable=False)
    id_setor = Column(Integer, ForeignKey("tipo_setores.id"), nullable=False)
    data_hora_inicio = Column(DateTime, nullable=False)
    data_hora_fim = Column(DateTime)
    # tempo_trabalhado = Column(DECIMAL(10,2))  # Campo não existe na tabela atual - será calculado dinamicamente
    status_apontamento = Column(String, nullable=False)
    foi_retrabalho = Column(Boolean, default=0)
    causa_retrabalho = Column(Integer, ForeignKey("tipo_causas_retrabalho.id"))
    observacao_os = Column(Text)
    servico_de_campo = Column(Boolean)
    observacoes_gerais = Column(Text)
    aprovado_supervisor = Column(Boolean)
    data_aprovacao_supervisor = Column(DateTime)
    supervisor_aprovacao = Column(Integer, ForeignKey("tipo_usuarios.id"))
    criado_por = Column(Integer, ForeignKey("tipo_usuarios.id"))
    criado_por_email = Column(String)
    data_processo_finalizado = Column(DateTime)
    setor = Column(String)  # Manter por compatibilidade
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
    supervisor_etapa_inicial = Column(Integer, ForeignKey("tipo_usuarios.id"))
    supervisor_etapa_parcial = Column(Integer, ForeignKey("tipo_usuarios.id"))
    supervisor_etapa_final = Column(Integer, ForeignKey("tipo_usuarios.id"))
    tipo_maquina = Column(Integer, ForeignKey("tipos_maquina.id"))
    tipo_atividade = Column(Integer, ForeignKey("tipo_atividade.id"))
    descricao_atividade = Column(Integer, ForeignKey("tipo_descricao_atividade.id"))
    categoria_maquina = Column(String)
    subcategorias_maquina = Column(Text)
    subcategorias_finalizadas = Column(Boolean, default=0)
    data_finalizacao_subcategorias = Column(DateTime)
    emprestimo_setor = Column(String)
    pendencia = Column(Boolean, default=0)
    pendencia_data = Column(DateTime)
    resultado_global = Column(String)  # Campo para resultado global do apontamento

    # Relacionamentos conforme hierarquia
    ordem_servico = relationship("OrdemServico", foreign_keys=[id_os], back_populates="apontamentos")
    usuario = relationship("Usuario", foreign_keys=[id_usuario])
    setor_obj = relationship("Setor", foreign_keys=[id_setor])
    causa_retrabalho_obj = relationship("TipoCausaRetrabalho", foreign_keys=[causa_retrabalho])
    supervisor_aprovacao_obj = relationship("Usuario", foreign_keys=[supervisor_aprovacao])
    criado_por_obj = relationship("Usuario", foreign_keys=[criado_por])
    supervisor_inicial_obj = relationship("Usuario", foreign_keys=[supervisor_etapa_inicial])
    supervisor_parcial_obj = relationship("Usuario", foreign_keys=[supervisor_etapa_parcial])
    supervisor_final_obj = relationship("Usuario", foreign_keys=[supervisor_etapa_final])
    tipo_maquina_obj = relationship("TipoMaquina", foreign_keys=[tipo_maquina])
    tipo_atividade_obj = relationship("TipoAtividade", foreign_keys=[tipo_atividade])
    descricao_atividade_obj = relationship("TipoDescricaoAtividade", foreign_keys=[descricao_atividade])

    # Relacionamentos reversos
    resultados_teste = relationship("ResultadoTeste", back_populates="apontamento")
    pendencias_origem = relationship("Pendencia", foreign_keys="[Pendencia.id_apontamento_origem]", back_populates="apontamento_origem")
    pendencias_fechamento = relationship("Pendencia", foreign_keys="[Pendencia.id_apontamento_fechamento]", back_populates="apontamento_fechamento")

class Pendencia(Base):
    __tablename__ = "pendencias"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    numero_os = Column(String, ForeignKey("ordens_servico.os_numero"), nullable=False)
    cliente = Column(String, nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    id_responsavel_inicio = Column(Integer, ForeignKey("tipo_usuarios.id"), nullable=False)
    tipo_maquina = Column(String, nullable=False)
    descricao_maquina = Column(Text, nullable=False)
    descricao_pendencia = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    prioridade = Column(String)
    data_fechamento = Column(DateTime)
    id_responsavel_fechamento = Column(Integer, ForeignKey("tipo_usuarios.id"))
    solucao_aplicada = Column(Text)
    observacoes_fechamento = Column(Text)
    id_apontamento_origem = Column(Integer, ForeignKey("apontamentos_detalhados.id"))
    id_apontamento_fechamento = Column(Integer, ForeignKey("apontamentos_detalhados.id"))
    tempo_aberto_horas = Column(Float)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)

    # Campos adicionados para performance e auditoria
    setor_origem = Column(String(100))  # Setor do responsável no momento da criação
    departamento_origem = Column(String(100))  # Departamento do responsável no momento da criação

    # Relacionamentos conforme hierarquia
    ordem_servico = relationship("OrdemServico", foreign_keys=[numero_os], back_populates="pendencias")
    responsavel_inicio = relationship("Usuario", foreign_keys=[id_responsavel_inicio])
    responsavel_fechamento = relationship("Usuario", foreign_keys=[id_responsavel_fechamento])
    apontamento_origem = relationship("ApontamentoDetalhado", foreign_keys=[id_apontamento_origem], back_populates="pendencias_origem")
    apontamento_fechamento = relationship("ApontamentoDetalhado", foreign_keys=[id_apontamento_fechamento], back_populates="pendencias_fechamento")

class Programacao(Base):
    __tablename__ = "programacoes"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    id_ordem_servico = Column(Integer, ForeignKey("ordens_servico.id"))
    criado_por_id = Column(Integer, ForeignKey("tipo_usuarios.id"), nullable=False)
    responsavel_id = Column(Integer, ForeignKey("tipo_usuarios.id"))
    observacoes = Column(Text)
    historico = Column(Text)  # Campo não editável para histórico de mudanças
    status = Column(String)
    inicio_previsto = Column(DateTime, nullable=False)
    fim_previsto = Column(DateTime, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    id_setor = Column(Integer, ForeignKey("tipo_setores.id"))

    # Relacionamentos conforme hierarquia
    ordem_servico = relationship("OrdemServico", foreign_keys=[id_ordem_servico], back_populates="programacoes")
    criado_por = relationship("Usuario", foreign_keys=[criado_por_id])
    responsavel = relationship("Usuario", foreign_keys=[responsavel_id])
    setor_obj = relationship("Setor", foreign_keys=[id_setor])

class ResultadoTeste(Base):
    __tablename__ = "resultados_teste"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    id_apontamento = Column(Integer, ForeignKey("apontamentos_detalhados.id"), nullable=False)
    id_teste = Column(Integer, ForeignKey("tipos_teste.id"), nullable=False)
    resultado = Column(String, nullable=False)
    observacao = Column(Text)
    data_registro = Column(DateTime)

    # Relacionamentos conforme hierarquia
    apontamento = relationship("ApontamentoDetalhado", foreign_keys=[id_apontamento], back_populates="resultados_teste")
    teste = relationship("TipoTeste", foreign_keys=[id_teste])

class OSTestesExclusivosFinalizados(Base):
    __tablename__ = "os_testes_exclusivos_finalizados"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    numero_os = Column(String, ForeignKey("ordens_servico.os_numero"), nullable=False)
    id_teste_exclusivo = Column(Integer, ForeignKey("tipos_teste.id"), nullable=False)
    nome_teste = Column(String, nullable=False)
    descricao_teste = Column(String)
    usuario_finalizacao = Column(Integer, ForeignKey("tipo_usuarios.id"), nullable=False)
    departamento = Column(String, nullable=False)
    setor = Column(String, nullable=False)
    data_finalizacao = Column(Date, nullable=False)
    hora_finalizacao = Column(Time, nullable=False)
    descricao_atividade = Column(Text)
    observacoes = Column(Text)
    data_criacao = Column(DateTime)

    # Relacionamentos conforme hierarquia
    ordem_servico = relationship("OrdemServico", foreign_keys=[numero_os])
    teste_exclusivo = relationship("TipoTeste", foreign_keys=[id_teste_exclusivo])
    usuario = relationship("Usuario", foreign_keys=[usuario_finalizacao])

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
    setor = Column(String, nullable=False)  # Manter por compatibilidade
    cargo = Column(String)
    departamento = Column(String, nullable=False)  # Manter por compatibilidade
    privilege_level = Column(String, nullable=False)
    is_approved = Column(Boolean, nullable=False)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    trabalha_producao = Column(Boolean, nullable=False)
    obs_reprovacao = Column(Text)
    id_setor = Column(Integer, ForeignKey("tipo_setores.id"))
    id_departamento = Column(Integer, ForeignKey("tipo_departamentos.id"))
    primeiro_login = Column(Boolean, nullable=False)

    # Relacionamentos
    setor_obj = relationship("Setor", foreign_keys=[id_setor], back_populates="usuarios")
    departamento_obj = relationship("Departamento", foreign_keys=[id_departamento], back_populates="usuarios")

class Setor(Base):
    __tablename__ = "tipo_setores"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    departamento = Column(String, nullable=False)  # Manter por compatibilidade
    descricao = Column(Text)
    ativo = Column(Boolean)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    id_departamento = Column(Integer, ForeignKey("tipo_departamentos.id"))
    area_tipo = Column(String, nullable=False)
    supervisor_responsavel = Column(Integer)
    permite_apontamento = Column(Boolean)

    # Relacionamentos
    departamento_obj = relationship("Departamento", foreign_keys=[id_departamento], back_populates="setores")
    usuarios = relationship("Usuario", foreign_keys="[Usuario.id_setor]", back_populates="setor_obj")

class Departamento(Base):
    __tablename__ = "tipo_departamentos"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nome_tipo = Column(String)
    descricao = Column(Text)
    ativo = Column(Boolean)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)

    # Relacionamentos
    setores = relationship("Setor", foreign_keys="[Setor.id_departamento]", back_populates="departamento_obj")
    usuarios = relationship("Usuario", foreign_keys="[Usuario.id_departamento]", back_populates="departamento_obj")

class TipoMaquina(Base):
    __tablename__ = "tipos_maquina"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nome_tipo = Column(String, nullable=False)
    categoria = Column(String)
    subcategoria = Column(Text)  # CORRIGIDO: usar Text em vez de JSON (dados são strings separadas por vírgula)
    descricao = Column(Text)
    ativo = Column(Boolean)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    id_departamento = Column(Integer, ForeignKey("tipo_departamentos.id"))
    especificacoes_tecnicas = Column(Text)  # Campo mantido por compatibilidade
    campos_teste_resultado = Column(Text)   # Campo mantido por compatibilidade
    setor = Column(String)                  # Manter por compatibilidade
    departamento = Column(Text)             # Manter por compatibilidade

    # Relacionamentos
    departamento_obj = relationship("Departamento", foreign_keys=[id_departamento])

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
    id_tipo_maquina = Column(Integer, ForeignKey("tipos_maquina.id"))
    # Campos de filtro por departamento e setor
    id_departamento = Column(Integer, ForeignKey("tipo_departamentos.id"))
    departamento = Column(String)
    setor = Column(String)

    # Relacionamentos conforme hierarquia
    tipo_maquina_obj = relationship("TipoMaquina", foreign_keys=[id_tipo_maquina])
    departamento_obj = relationship("Departamento", foreign_keys=[id_departamento])

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
    # Campos de filtro por departamento
    id_departamento = Column(Integer, ForeignKey("tipo_departamentos.id"))
    departamento = Column(String)
    tipo_maquina = Column(Integer, ForeignKey("tipos_maquina.id"))

    # Relacionamentos conforme hierarquia
    departamento_obj = relationship("Departamento", foreign_keys=[id_departamento])
    tipo_maquina_obj = relationship("TipoMaquina", foreign_keys=[tipo_maquina])

class TipoCausaRetrabalho(Base):
    __tablename__ = "tipo_causas_retrabalho"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    codigo = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    ativo = Column(Boolean)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    id_departamento = Column(Integer, ForeignKey("tipo_departamentos.id"))
    departamento = Column(Text)
    setor = Column(Text)

    # Relacionamentos conforme hierarquia
    departamento_obj = relationship("Departamento", foreign_keys=[id_departamento])

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
    tipo_maquina = Column(Integer, ForeignKey("tipos_maquina.id"))
    teste_exclusivo_setor = Column(Boolean)
    descricao_teste_exclusivo = Column(String)
    categoria = Column(String)
    subcategoria = Column(Integer)

    # Relacionamentos conforme hierarquia
    tipo_maquina_obj = relationship("TipoMaquina", foreign_keys=[tipo_maquina])

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

class TipoFeriados(Base):
    __tablename__ = "tipo_feriados"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    data_feriado = Column(Date, nullable=False)
    tipo = Column(String)  # Nacional, Estadual, Municipal
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    observacoes = Column(Text)

class TipoFalha(Base):
    __tablename__ = "tipo_falha"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    codigo = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    categoria = Column(String)
    severidade = Column(String)  # BAIXA, MEDIA, ALTA, CRITICA
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
    id_departamento = Column(Integer, ForeignKey("tipo_departamentos.id"))
    setor = Column(String)
    observacoes = Column(Text)
    # Campo de filtro por departamento (nome)
    departamento = Column(String)

    # Relacionamentos conforme hierarquia
    departamento_obj = relationship("Departamento", foreign_keys=[id_departamento])

# Aliases para compatibilidade
TipoUsuario = Usuario
OSTesteExclusivoFinalizado = OSTestesExclusivosFinalizados
