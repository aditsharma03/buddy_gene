import os
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt, JWTError

from storage import read_users, write_users



router = APIRouter(prefix="/auth", tags=["Auth"])



JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str) -> str:
    return pwd_context.hash(password.strip())


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password.strip(), password_hash)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_user_by_email(email: str):
    users = read_users()
    return next((u for u in users if u["email"] == email), None)



class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    success: bool
    token: str



@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest):
    users = read_users()
    email = normalize_email(req.email)

    if get_user_by_email(email):
        raise HTTPException(
            status_code=409,
            detail="User already exists"
        )

    users.append({
        "name": req.name.strip(),
        "email": email,
        "passwordHash": hash_password(req.password),
        "createdAt": datetime.utcnow().isoformat(),
    })

    write_users(users)

    return {"success": True}



@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest):
    email = normalize_email(req.email)
    user = get_user_by_email(email)

    if not user or not verify_password(req.password, user["passwordHash"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token({
        "email": user["email"],
        "name": user["name"],
    })

    return {
        "success": True,
        "token": token,
    }

def get_current_user(token: str = Depends(lambda: None)):
    if not token:
        raise HTTPException(status_code=401, detail="Token missing")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
