from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database.database import get_db
from .schema import UserCreate, UserResponse, Token, UserLogin
from .service import AuthService
from .dependencies import get_current_active_user, require_admin, require_teacher_or_admin
from .models.model import User

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur"""
    return AuthService.register_user(db, user_data)

@router.post("/login", response_model=Token)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Connexion d'un utilisateur"""
    return AuthService.login_user(db, login_data)

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Endpoint compatible OAuth2"""
    login_data = UserLogin(username=form_data.username, password=form_data.password)
    return AuthService.login_user(db, login_data)

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_active_user)):
    """Récupère les informations de l'utilisateur connecté"""
    return current_user

@router.get("/users", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_admin)
):
    """Liste tous les utilisateurs (admin seulement)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_admin)
):
    """Désactive un utilisateur (admin seulement)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.commit()
    
    return {"message": "User deactivated successfully"}
