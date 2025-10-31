from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional
import os
from datetime import datetime, timedelta
from ..database.database import get_db
from .models.model import User, UserRole
from .schema import TokenData
from passlib.context import CryptContext


# Configuration JWT
SECRET_KEY = os.getenv("SECRET_KEY", "${SECERET_KEY}")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# Configuration du hachage des mots de passe
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_strength(password: str) -> dict:
    """
    Vérifie la force du mot de passe.
    Args:
        password: Mot de passe à vérifier
    Returns:
        dict: Informations sur la force du mot de passe
    """
    checks = {
        "length": len(password) >= 8,
        "uppercase": any(c.isupper() for c in password),
        "lowercase": any(c.islower() for c in password),
        "digit": any(c.isdigit() for c in password),
        "special": any(not c.isalnum() for c in password),
        "not_too_long": len(password.encode('utf-8')) <= 72
    }
    
    strength = "weak"
    score = sum(checks.values())
    
    if score >= 5:
        strength = "strong"
    elif score >= 3:
        strength = "medium"
    
    return {
        "strength": strength,
        "score": score,
        "checks": checks,
        "valid": all(checks.values())
    }

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe correspond au hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash le mot de passe avec bcrypt"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un token JWT"""
    to_encode = data.copy()
    
    # Convertir les enums en strings pour la sérialisation JSON
    for key, value in to_encode.items():
        if hasattr(value, 'value'):
            to_encode[key] = value.value
        elif isinstance(value, UserRole):
            to_encode[key] = value.value
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Récupère l'utilisateur courant à partir du token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        
        if username is None or user_id is None:
            raise credentials_exception
        
        token_data = TokenData(username=username, user_id=user_id, role=role)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Vérifie que l'utilisateur est actif"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Dépendances pour les rôles
# S'assurer que les rôles sont cohérents
def require_role(required_role: UserRole):
    def role_checker(current_user: User = Depends(get_current_active_user)):
         # Convertir en string pour la comparaison
        current_user_role = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
        required_role_value = required_role.value
        
        if current_user_role != required_role_value:
            if current_user_role != UserRole.admin.value:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires {required_role_value} role"
                )
        return current_user
    return role_checker

# Dépendances spécifiques par rôle
require_student = require_role(UserRole.student)
require_teacher = require_role(UserRole.teacher)
require_admin = require_role(UserRole.admin)

def require_teacher_or_admin(current_user: User = Depends(get_current_active_user)):
    """Autorise les enseignants et admins"""
    if current_user.role not in [UserRole.teacher, UserRole.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires teacher or admin role"
        )
    return current_user

def require_same_class_or_teacher(class_id: int, current_user: User = Depends(get_current_active_user)):
    """Vérifie que l'utilisateur a accès à la classe"""
    # Les admins ont accès à tout
    if current_user.role == UserRole.admin.value:
        return current_user
    
    # Les étudiants n'ont accès qu'à leur propre classe
    if current_user.role == UserRole.student.value:
        if current_user.class_id == class_id:
            return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied to this class"
    )