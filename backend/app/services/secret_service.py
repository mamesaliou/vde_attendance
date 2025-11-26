import os
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from app.core.config import settings
from app.tools.singleton import Singleton

class SecretService(metaclass=Singleton):
    
    def __init__(self):
        self._private_key = None
        self._public_key = None
        self._private_key_pem = None
        self._public_key_pem = None
        self.generate_keys()
    
    def load_private_key(self):
        if self._private_key is None:
            try:
                private_key_path = Path(settings.PRIVATE_KEY_PATH)
                
                if not private_key_path.exists():
                    raise FileNotFoundError(f"Clé privée introuvable: {private_key_path}")
                
                with open(private_key_path, "rb") as key_file:
                    password = settings.PRIVATE_KEY_PASSWORD.encode() if settings.PRIVATE_KEY_PASSWORD else None
                    
                    self._private_key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=password,
                        backend=default_backend()
                    )
                    
            except Exception as e:
                raise RuntimeError(f"Erreur chargement clé privée: {e}")
        
        return self._private_key
    
    def load_public_key(self):
        if self._public_key is None:
            try:
                public_key_path = Path(settings.PUBLIC_KEY_PATH)
                
                if not public_key_path.exists():
                    raise FileNotFoundError(f"Clé publique introuvable: {public_key_path}")
                
                with open(public_key_path, "rb") as key_file:
                    self._public_key = serialization.load_pem_public_key(
                        key_file.read(),
                        backend=default_backend()
                    )
            except Exception as e:
                raise RuntimeError(f"Erreur chargement clé publique: {e}")
        
        return self._public_key
    
    def get_private_key_pem(self) -> str:
        if self._private_key_pem is None:
            private_key = self.load_private_key()
            self._private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode('utf-8')
        
        return self._private_key_pem

    def get_public_key_pem(self) -> str:
        if self._public_key_pem is None:
            public_key = self.load_public_key()
            self._public_key_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
        
        return self._public_key_pem

    @staticmethod
    def keys_exist() -> bool:
        private_path = Path(settings.PRIVATE_KEY_PATH)
        public_path = Path(settings.PUBLIC_KEY_PATH)
        return private_path.exists() and public_path.exists()

    def generate_keys(self, key_size: int = 2048, password: str = None, force: bool = False) -> bool:
        private_path = Path(settings.PRIVATE_KEY_PATH)
        public_path = Path(settings.PUBLIC_KEY_PATH)
        
        if (private_path.exists() and public_path.exists()) and not force:
            return
        
        try:
            private_path.parent.mkdir(parents=True, exist_ok=True)
            public_path.parent.mkdir(parents=True, exist_ok=True)
            
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            
            public_key = private_key.public_key()
            
            if password:
                encryption_algorithm = serialization.BestAvailableEncryption(password.encode())
            else:
                encryption_algorithm = serialization.NoEncryption()
            
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption_algorithm
            )
            
            with open(private_path, 'wb') as f:
                f.write(private_pem)
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            with open(public_path, 'wb') as f:
                f.write(public_pem)
            
            if os.name != 'nt':
                os.chmod(private_path, 0o600)
                os.chmod(public_path, 0o644)
            
            self._private_key = None
            self._public_key = None
            self._private_key_pem = None
            self._public_key_pem = None
            
            return True
            
        except Exception as e:
            if private_path.exists():
                private_path.unlink()
            if public_path.exists():
                public_path.unlink()
            raise RuntimeError(f"Erreur génération des clés: {e}")

    def generate_keys_if_missing(self, key_size: int = 2048) -> bool:
        if not self.keys_exist():
            return self.generate_keys(key_size=key_size)
        return False


secret_service = SecretService()
