from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

class Config:
    """Configuration globale pour le middleware d'authentification."""
    
    # Chargement des variables d'environnement depuis .env
    load_dotenv()
    
    # Configuration JWT
    JWT_PUBLIC_KEY: str = os.getenv('JWT_PUBLIC_KEY', 'your-secret-key')

    
    # Configuration de l'audit
    AUDIT_ENABLED: bool = os.getenv('AUDIT_ENABLED', 'True').lower() == 'true'
    AUDIT_LOG_PATH: Optional[str] = os.getenv('AUDIT_LOG_PATH')
    


    
    # Configuration des endpoints d'API pour chaque type d'utilisateur
    PUBLIC_USER_API_ENDPOINT: str = os.getenv('PUBLIC_USER_API_ENDPOINT')
    PRO_USER_API_ENDPOINT: str = os.getenv('PRO_USER_API_ENDPOINT')
    SIDE_ADMIN_API_ENDPOINT: str = os.getenv('SIDE_ADMIN_API_ENDPOINT')
    PERMISSIONS_API_TIMEOUT: int = int(os.getenv('PERMISSIONS_API_TIMEOUT', 10))
        
        