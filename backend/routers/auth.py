"""
Autenticação - Login, Logout, Perfil
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from backend.models.schemas import LoginRequest, TokenResponse
from backend.config import settings
from backend import database as db

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

SECRET_KEY = settings.APP_SECRET_KEY
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency para obter o usuário atual a partir do JWT."""
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")

    sb = db.get_supabase()
    result = sb.table("users").select("*, companies(*)").eq("id", user_id).maybe_single().execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return result.data


async def get_superadmin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency: apenas SuperAdmin pode passar."""
    if current_user.get("role") != "superadmin" and current_user.get("id") != settings.SUPERADMIN_ID:
        raise HTTPException(status_code=403, detail="Acesso restrito ao SuperAdmin")
    return current_user


async def get_admin_or_above(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency: admin ou superior."""
    if current_user.get("role") not in ("superadmin", "admin"):
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return current_user


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login com email e senha. Retorna JWT."""
    sb = db.get_supabase()
    result = sb.table("users").select("*, companies(*)").eq("email", request.email).maybe_single().execute()

    user = result.data
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not verify_password(request.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    company_data = user.get("companies") or {}
    if company_data and not company_data.get("is_active", True):
        raise HTTPException(status_code=403, detail="Empresa suspensa ou inativa")

    # Marca usuário como online
    sb.table("users").update({"is_online": True}).eq("id", user["id"]).execute()

    token = create_access_token({
        "sub": user["id"],
        "company_id": user.get("company_id"),
        "role": user.get("role"),
    })

    await db.create_log(user.get("company_id"), "user_login", {"email": user["email"]}, user["id"])

    # Remove hash da senha antes de retornar
    user.pop("password_hash", None)

    return TokenResponse(access_token=token, user=user)


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout - marca usuário como offline."""
    sb = db.get_supabase()
    sb.table("users").update({"is_online": False}).eq("id", current_user["id"]).execute()
    return {"message": "Logout realizado com sucesso"}


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Retorna dados do usuário atual."""
    current_user.pop("password_hash", None)
    return current_user
