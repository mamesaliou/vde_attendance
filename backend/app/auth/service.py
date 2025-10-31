from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .model import User, UserRole
from .schema import UserCreate, UserLogin
from .dependencies import get_password_strength, verify_password, get_password_hash, create_access_token
from datetime import timedelta

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user
    
    @staticmethod
    def register_user(db: Session, user_data: UserCreate):
        # Vérifier si l'email existe déjà
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Vérifier si le username existe déjà
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Vérifier les contraintes de rôle
        if user_data.role == UserRole.student.value and not user_data.class_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Students must be assigned to a class"
            )
        
        # Vérifier la force du mot de passe
        password_strength = get_password_strength(user_data.password)
        if not password_strength["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password too weak",
                headers={"X-Password-Strength": password_strength["strength"]}
            )
        
        # Créer l'utilisateur
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role
        )
        
        db.add(db_user)
        db.flush()  # Pour obtenir l'ID
        
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def login_user(db: Session, login_data: UserLogin):
        user = AuthService.authenticate_user(db, login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Créer le token d'accès
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "role": user.role
            },
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }