"""
Script para corrigir a tabela produtos tornando evento_id opcional
conforme a regra de negócio que produtos não devem ser atrelados a eventos
"""
import os
import sys
sys.path.append(os.getcwd())
from app.database import get_db
from sqlalchemy import text

def fix_produtos_evento_id():
    """Tornar evento_id opcional na tabela produtos"""
    db = next(get_db())
    
    try:
        print("🔧 Iniciando correção da tabela produtos...")
        
        # SQL para tornar evento_id opcional
        sql_fix = """
        ALTER TABLE produtos 
        ALTER COLUMN evento_id DROP NOT NULL;
        """
        
        print("📝 Executando: ALTER TABLE produtos ALTER COLUMN evento_id DROP NOT NULL")
        db.execute(text(sql_fix))
        db.commit()
        
        print("✅ Correção concluída! evento_id agora é opcional")
        
        # Verificar a alteração
        sql_check = """
        SELECT column_name, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'produtos' AND column_name = 'evento_id';
        """
        
        result = db.execute(text(sql_check)).fetchone()
        if result:
            nullable_status = "NULL" if result[1] == 'YES' else "NOT NULL"
            print(f"🔍 Verificação: evento_id agora é {nullable_status}")
        
    except Exception as e:
        print(f"❌ Erro ao executar correção: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = fix_produtos_evento_id()
    if success:
        print("\n🎉 Correção bem-sucedida! Agora produtos podem ser criados sem evento_id")
    else:
        print("\n💥 Falha na correção!")
