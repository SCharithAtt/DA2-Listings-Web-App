from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional

from app.db.mongo import get_db
from app.models.user import UserCreate, UserLogin, TokenResponse, Role
from app.auth.security import hash_password, verify_password, create_access_token, decode_access_token


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload["sub"]


async def get_current_role(token: str = Depends(oauth2_scheme)) -> Role:
    payload = decode_access_token(token)
    if not payload or "role" not in payload:
        # default to user for older tokens
        return Role.user
    try:
        return Role(payload["role"])
    except Exception:
        return Role.user


@router.post("/register", response_model=TokenResponse)
async def register(user: UserCreate, db=Depends(get_db)):
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(user.password)
    # default role is user
    res = await db.users.insert_one({"email": user.email, "hashed_password": hashed, "role": Role.user.value})
    user_id = str(res.inserted_id)
    token = create_access_token(user_id, extra_claims={"role": Role.user.value})
    return TokenResponse(access_token=token, role=Role.user)


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user.get("hashed_password")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    role = user.get("role") or Role.user.value
    token = create_access_token(str(user.get("_id")), extra_claims={"role": role})
    return TokenResponse(access_token=token, role=Role(role))
