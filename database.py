from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./agendamentos.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() 

from models import Agendamento

from datetime import time, date

def criar_agendamento_teste():
    db = SessionLocal()
    existente = db.query(Agendamento).filter(
        Agendamento.data == date(2025, 6, 20),
        Agendamento.hora == time(15, 0)
    ).first()

    if not existente:
        agendamento = Agendamento(
            nome="Teste Inicial",
            email="teste@email.com",
            data=date(2025, 6, 20),
            hora=time(15, 0)
        )
        db.add(agendamento)
        db.commit()
        db.refresh(agendamento)

    db.close()

# criar_agendamento_teste()
