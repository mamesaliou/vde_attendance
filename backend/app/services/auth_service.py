from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import HTTPException, status
from fastapi import Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database.models.user_model import User, UserRole
from ..api.v1.schemas.user_schemas import UserCreate, UserLogin, UserResponse
from ..api.deps import add_to_blacklist, get_password_strength, verify_password, get_password_hash, create_access_token, require_admin, verify_token
from ..database.database import get_db

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
    
    @staticmethod
    def list_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(require_admin)
    ):
        users = db.query(User).offset(skip).limit(limit).all()
        return users

    @staticmethod
    def deactive_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: UserResponse = Depends(require_admin)
    ):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_active = False
        db.commit()
        
        return {"message": "User deactivated successfully"}
    
    @staticmethod
    def logout_by_cookies(response: Response):
        # Supprimer les cookies d'authentification
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Déconnexion réussie"}
        )        

    @staticmethod
    def logout_by_token(token: str, current_user: UserResponse):
        try:
            

            #get_current_token(token)

            #Verifier si le token est dans la blackliste
            verify_token(token)

            # Ajouter le token à la blacklist
            add_to_blacklist(token.credentials)
            
            # Logger la déconnexion
            # print(f"Utilisateur {current_user.get('sub', 'Unknown')} déconnecté")
            print(f"Utilisateur {current_user.first_name} {current_user.last_name} est déconnecté")

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Déconnexion réussie",
                    "detail": "Le token a été invalidé"
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Erreur lors de la déconnexion: {str(e)}"
            )