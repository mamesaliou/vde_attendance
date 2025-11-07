from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from ....database.database import get_db
from ..schemas.user_schemas import UserCreate, UserResponse, Token, UserLogin
from ....services.auth_service import AuthService
from ...deps import get_current_active_user, require_admin, require_teacher_or_admin
from ....database.models.user_model import User

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur"""
    return AuthService.register_user(db, user_data)

@router.post("/login", response_model=Token)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Connexion d'un utilisateur"""
    return AuthService.login_user(db, login_data)

@router.post("/logoutbc", response_model=Token)
async def logout_by_cookies(response: Response):
    """Route de déconnexion avec suppression des cookies"""
    return AuthService.logout_by_cookies(response)
    

@router.post("/logoutbt", response_model=Token)
def logout_by_token(
    token: str = Depends(security),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Route de déconnexion avec invalidation du token JWT"""
    return AuthService.logout_by_token(token, current_user)

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
    return AuthService.list_users(skip, limit, db, current_user)

@router.put("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(require_admin)
):
    """Désactive un utilisateur (admin seulement)"""
    return AuthService.deactive_user(user_id, db, current_user)
