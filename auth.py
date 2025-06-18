from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta


SECRET_KEY = "fast-api-web-2"
ALGORITHM = "HS256"
ACESSO_EXPIRA_EM_MINUTOS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificar_senha(senha_pura, senha_hash):
    return pwd_context.verify(senha_pura, senha_hash)

def gerar_hash_senha(senha):
    return pwd_context.hash(senha)

def criar_token_acesso(dados: dict):
    to_encode = dados.copy()
    expira = datetime.utcnow() + timedelta(minutes=ACESSO_EXPIRA_EM_MINUTOS)
    to_encode.update({"exp": expira})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
