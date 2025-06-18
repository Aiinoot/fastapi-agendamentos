from sqlalchemy.orm import Session
from models import Agendamento, Usuario
from schemas import AgendamentoCreate, UsuarioCreate
from auth import gerar_hash_senha, verificar_senha
from sqlalchemy.exc import SQLAlchemyError


def criar_agendamento(db: Session, agendamento: AgendamentoCreate):
    try:
        conflito = db.query(Agendamento).filter(
            Agendamento.data == agendamento.data,
            Agendamento.hora == agendamento.hora,
            Agendamento.status != "cancelado"
        ).first()

        if conflito:
            return None

        novo_agendamento = Agendamento(
            nome=agendamento.nome,
            email=agendamento.email,
            data=agendamento.data,
            hora=agendamento.hora,
            status="agendado"
        )

        db.add(novo_agendamento)
        db.commit()
        db.refresh(novo_agendamento)
        return novo_agendamento

    except SQLAlchemyError as e:
        db.rollback()
        print(f"[ERRO] Erro ao criar agendamento: {e}")
        return None


def listar_agendamentos(db: Session):
    try:
        return db.query(Agendamento).filter(Agendamento.status != "cancelado").all()
    except SQLAlchemyError as e:
        print(f"[ERRO] Erro ao listar agendamentos: {e}")
        return []


def obter_agendamento(db: Session, agendamento_id: int):
    try:
        return db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    except SQLAlchemyError as e:
        print(f"[ERRO] Erro ao obter agendamento: {e}")
        return None


def cancelar_agendamento(db: Session, agendamento_id: int):
    try:
        agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
        if not agendamento:
            return None

        if agendamento.status == "cancelado":
            return agendamento  

        agendamento.status = "cancelado"
        db.commit()
        db.refresh(agendamento)
        return agendamento
    except SQLAlchemyError as e:
        db.rollback()
        print(f"[ERRO] Erro ao cancelar agendamento: {e}")
        return None


def confirmar_agendamento(db: Session, agendamento_id: int):
    try:
        agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
        if not agendamento:
            return None

        if agendamento.status == "cancelado":
            return None  

        agendamento.status = "confirmado"
        db.commit()
        db.refresh(agendamento)
        return agendamento
    except SQLAlchemyError as e:
        db.rollback()
        print(f"[ERRO] Erro ao confirmar agendamento: {e}")
        return None

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

def get_usuario_logado(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    dados = verificar_token(token)
    if not dados:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")

    usuario = db.query(Usuario).filter(Usuario.email == dados.get("sub")).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado.")
    
    return usuario