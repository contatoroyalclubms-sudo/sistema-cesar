
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from app.models.meep_models import MEEPEvento, MEEPParticipante, MEEPCaptura, MEEPAnalytics
from app.models import Base

print("Criando tabelas MEEP...")
Base.metadata.create_all(bind=engine)
print("Tabelas criadas com sucesso!")
