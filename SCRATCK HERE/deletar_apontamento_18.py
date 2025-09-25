#!/usr/bin/env python3
import sys
import os

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

from config.database_config import get_db
from sqlalchemy import text
from app.database_models import ApontamentoDetalhado

def deletar_apontamento_18():
    try:
        db = next(get_db())
        
        # Primeiro, verificar se o apontamento ID 18 existe
        apontamento = db.query(ApontamentoDetalhado).filter(ApontamentoDetalhado.id == 18).first()
        
        if apontamento:
            print("🔍 Apontamento encontrado:")
            print(f"  ID: {apontamento.id}")
            print(f"  OS: {apontamento.id_os}")
            print(f"  Usuário: {apontamento.id_usuario}")
            print(f"  Setor: {apontamento.id_setor}")
            print(f"  Data início: {apontamento.data_hora_inicio}")
            print(f"  Data fim: {apontamento.data_hora_fim}")
            print(f"  Status: {apontamento.status_apontamento}")
            print(f"  Observação: {apontamento.observacao_os}")
            
            # Confirmar se é realmente o registro correto
            if (apontamento.id_setor == 1 and 
                apontamento.id_usuario == 1 and 
                apontamento.status_apontamento == "FINALIZADO" and
                "Edição de apontamento pendente" in str(apontamento.observacoes_gerais or "")):
                
                print("\n✅ Confirmado: Este é o apontamento correto para deletar")
                
                # Deletar o apontamento
                db.delete(apontamento)
                db.commit()
                
                print("🗑️ Apontamento ID 18 deletado com sucesso!")
                
                # Verificar se foi realmente deletado
                verificacao = db.query(ApontamentoDetalhado).filter(ApontamentoDetalhado.id == 18).first()
                if verificacao is None:
                    print("✅ Confirmado: Apontamento foi removido do banco de dados")
                else:
                    print("❌ Erro: Apontamento ainda existe no banco")
                    
            else:
                print("⚠️ ATENÇÃO: O apontamento encontrado não corresponde exatamente aos dados fornecidos")
                print("   Não será deletado por segurança")
                
        else:
            print("❌ Apontamento ID 18 não encontrado no banco de dados")
            
        # Mostrar estatísticas atualizadas
        total_apontamentos = db.query(ApontamentoDetalhado).count()
        print(f"\n📊 Total de apontamentos restantes: {total_apontamentos}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()

if __name__ == "__main__":
    deletar_apontamento_18()
