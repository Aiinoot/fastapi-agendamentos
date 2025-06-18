from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import criar_token_acesso, verificar_token

from database import SessionLocal, engine
from models import Base
import crud
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Agendamentos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rotas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_usuario_logado(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    dados = verificar_token(token)
    if not dados:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")

    usuario = db.query(Usuario).filter(Usuario.email == dados.get("sub")).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado.")
    
    return usuario

@app.post("/agendamentos", response_model=schemas.Agendamento)
def criar_agendamento(
    agendamento: schemas.AgendamentoCreate,
    db: Session = Depends(get_db),
    usuario: schemas.Usuario = Depends(get_usuario_logado)
):
    novo = crud.criar_agendamento(db, agendamento)
    if not novo:
        raise HTTPException(status_code=400, detail="Horário já agendado ou erro ao salvar.")
    return novo


@app.get("/agendamentos", response_model=list[schemas.Agendamento])
def listar_agendamentos(db: Session = Depends(get_db)):
    try:
        return crud.listar_agendamentos(db)
    except Exception:
        raise HTTPException(status_code=500, detail="Erro ao listar agendamentos.")


@app.get("/agendamentos/{agendamento_id}", response_model=schemas.Agendamento)
def obter_agendamento(agendamento_id: int, db: Session = Depends(get_db)):
    agendamento = crud.obter_agendamento(db, agendamento_id)
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")
    return agendamento


@app.put("/agendamentos/{agendamento_id}/cancelar", response_model=schemas.Agendamento)
def cancelar_agendamento(agendamento_id: int, db: Session = Depends(get_db)):
    agendamento = crud.cancelar_agendamento(db, agendamento_id)
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado ou erro ao cancelar.")
    return agendamento


@app.put("/agendamentos/{agendamento_id}/confirmar", response_model=schemas.Agendamento)
def confirmar_agendamento(agendamento_id: int, db: Session = Depends(get_db)):
    agendamento = crud.confirmar_agendamento(db, agendamento_id)
    if not agendamento:
        raise HTTPException(status_code=400, detail="Não é possível confirmar um agendamento cancelado ou inexistente.")
    return agendamento


@app.post("/usuarios", response_model=schemas.Usuario)
def registrar(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    novo = crud.criar_usuario(db, usuario)
    if not novo:
        raise HTTPException(status_code=400, detail="Email já cadastrado.")
    return novo

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = crud.autenticar_usuario(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    
    token = criar_token_acesso({"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}