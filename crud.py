from sqlalchemy.orm import Session
from models import Agendamento, Usuario
from schemas import AgendamentoCreate, UsuarioCreate
from auth import gerar_hash_senha, verificar_senha
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Agendamento

def criar_agendamento(db: Session, agendamento: AgendamentoCreate, usuario_id: int):
    try:
        print("→ Verificando conflito com:")
        print("Data:", agendamento.data)
        print("Hora:", agendamento.hora)
        print("Usuário:", usuario_id)
        conflito = db.query(Agendamento).filter(
            Agendamento.data == agendamento.data,
            Agendamento.hora == agendamento.hora,
            Agendamento.usuario_id == usuario_id,
            Agendamento.status != "cancelado"
        ).first()

        if conflito:
            return None

        novo_agendamento = Agendamento(
            nome=agendamento.nome,
            email=agendamento.email,
            data=agendamento.data,
            hora=agendamento.hora,
            status="agendado",
            usuario_id=usuario_id
        )

        db.add(novo_agendamento)
        db.commit()
        db.refresh(novo_agendamento)
        return novo_agendamento

    except SQLAlchemyError as e:
        db.rollback()
        print(f"[ERRO] Erro ao criar agendamento: {e}")
        return None

def listar_agendamentos_por_usuario(db: Session, usuario_id: int):
    try:
        return db.query(Agendamento).filter(Agendamento.usuario_id == usuario_id).all()
    except SQLAlchemyError as e:
        print(f"[ERRO] Erro ao listar agendamentos: {e}")
        return []

def criar_usuario(db: Session, usuario: UsuarioCreate):
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        return None

    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha=gerar_hash_senha(usuario.senha)
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

def autenticar_usuario(db: Session, email: str, senha: str):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not verificar_senha(senha, usuario.senha):
        return None
    return usuario

def obter_agendamento(db: Session, agendamento_id: int):
    return db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()

def confirmar_agendamento(db: Session, agendamento_id: int):
    agendamento = obter_agendamento(db, agendamento_id)
    if agendamento and agendamento.status != "cancelado":
        agendamento.status = "confirmado"
        db.commit()
        db.refresh(agendamento)
        return agendamento
    return None

def cancelar_agendamento(db: Session, agendamento_id: int):
    agendamento = obter_agendamento(db, agendamento_id)
    if agendamento and agendamento.status != "cancelado":
        agendamento.status = "cancelado"
        db.commit()
        db.refresh(agendamento)
        return agendamento
    return None