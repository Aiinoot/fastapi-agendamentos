from pydantic import BaseModel, EmailStr
from datetime import date, time

class AgendamentoBase(BaseModel):
    nome: str
    email: EmailStr
    data: date
    hora: time

class AgendamentoCreate(AgendamentoBase):
    pass

class Agendamento(AgendamentoBase):
    id: int
    status: str
    usuario_id: int

    class Config:
        orm_mode = True

class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    senha: str

class Usuario(UsuarioBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

