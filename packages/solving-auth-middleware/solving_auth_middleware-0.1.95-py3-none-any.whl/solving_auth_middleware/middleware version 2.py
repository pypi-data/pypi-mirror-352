from flask import request, jsonify, current_app, make_response
from functools import wraps
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity,

)

from flask_jwt_extended.exceptions import (
    JWTExtendedException,
    JWTDecodeError,
    InvalidHeaderError,
    InvalidQueryParamError,
    NoAuthorizationError,
    CSRFError,
    WrongTokenError,
    RevokedTokenError,
    FreshTokenRequired,
    UserLookupError,
    UserClaimsVerificationError
)
import requests
from typing import Optional, List, Callable, Dict

from solving_auth_middleware.enums import UserTypeEnum

# --- Ajout : import des fonctions de vérification d'accès ressource ---
try:
    from app.utils.permission_verification import (
        verify_pro_user_access_to_patient,
        verify_public_user_access_to_patient,
        verify_user_admin_access,
    )
except ImportError:
    # fallback pour éviter l'erreur si le code n'est pas dans le même projet
    verify_pro_user_access_to_patient = None
    verify_public_user_access_to_patient = None
    verify_user_admin_access = None

def verify_permissions_from_api(identity: str, endpoint: str, token: str, permissions: List[str]) -> bool:
    """Vérifie les permissions auprès de l'API de permissions."""
    try:
        response = requests.post(
            endpoint,
            json={'identity': identity, 'permissions': permissions},
            headers={'Authorization': f'Bearer {token}'},
            timeout=current_app.config.get('PERMISSIONS_API_TIMEOUT', 10)
        )
        return response.status_code == 200
    except requests.RequestException:
        return False

def verify_permissions_from_function(identity: str, function: Callable, permissions: List[str]) -> bool:
    """Vérifie les permissions auprès de la fonction."""
    return function(identity, permissions)

def requires_permissions(
    user_type: UserTypeEnum = UserTypeEnum.PRO,
    location: str = 'headers',
    fresh: bool = False,
    audit_fn: Optional[Callable] = None,
    verify_fn: Optional[Callable] = None,
    required_permissions: Optional[List[str]] = None,
    resource_check_fn: Optional[Callable] = None,
    resource_args: Optional[Dict] = None,
):
    """
    Décorateur pour vérifier les permissions ET l'accès à la ressource.
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required(locations=[location], fresh=fresh)
        def decorator(*args, **kwargs):
            try:
                jwt_data = get_jwt()
                identity = get_jwt_identity()
                token = request.headers.get('Authorization', '').split(' ')[1]
                current_app.logger.info(f"Token: {token}")
                current_app.logger.info(f"Identity: {identity}")
                current_app.logger.info(f"Required permissions: {required_permissions}")
                # 1. Vérification des permissions
                if verify_fn is not None:

                    if not verify_permissions_from_function(identity, verify_fn, required_permissions or []):
                        return {"msg": f"Insufficient permissions for {user_type.value} user"}, 403
                else:
                    endpoint = current_app.config.get(f'{user_type.value.upper()}_USER_API_ENDPOINT')
                    if not endpoint:
                        return {"msg": f"Invalid user type: {user_type.value}"}, 400
                    if not verify_permissions_from_api(identity, endpoint, token, required_permissions or []):
                        return {"msg": f"Insufficient permissions for {user_type.value} user"}, 403
                # 2. Vérification d'accès à la ressource (si applicable)
                if resource_check_fn is not None:
                    # Les arguments pour la ressource peuvent venir de resource_args ou kwargs
                    args_to_pass = resource_args or {}
                    # On ajoute l'identity si la fonction l'attend
                    if user_type == UserTypeEnum.PRO:
                        # pro_user doit accéder à un patient
                        if not resource_check_fn(identity, **args_to_pass):
                            return {"msg": "Access to patient resource denied for pro user."}, 403
                    elif user_type == UserTypeEnum.PUBLIC:
                        # public_user doit accéder à son propre patient
                        if not resource_check_fn(identity, **args_to_pass):
                            return {"msg": "Access to patient resource denied for public user."}, 403
                    elif user_type == UserTypeEnum.USER_ADMIN:
                        # user_admin doit être admin
                        if not resource_check_fn(identity, **args_to_pass):
                            return {"msg": "Access denied for user admin."}, 403
                # Audit si nécessaire
                if audit_fn:
                    audit_fn(identity, request)
            except NoAuthorizationError as e:
                return {"msg": "Missing authorization token", "error": str(e)}, 401
            except JWTDecodeError as e:
                return {"msg": "Invalid token format", "error": str(e)}, 401
            except InvalidHeaderError as e:
                return {"msg": "Invalid authorization header", "error": str(e)}, 401
            except InvalidQueryParamError as e:
                return {"msg": "Invalid token in query parameters", "error": str(e)}, 401
            except CSRFError as e:
                return {"msg": "CSRF protection failed", "error": str(e)}, 401
            except WrongTokenError as e:
                return {"msg": "Wrong token type used", "error": str(e)}, 401
            except RevokedTokenError as e:
                return {"msg": "Token has been revoked", "error": str(e)}, 401
            except FreshTokenRequired as e:
                return {"msg": "Fresh token required", "error": str(e)}, 401
            except UserLookupError as e:
                return {"msg": "User not found", "error": str(e)}, 401
            except UserClaimsVerificationError as e:
                return {"msg": "Invalid user claims", "error": str(e)}, 401
            except requests.RequestException as e:
                return {"msg": "Permission service unavailable", "error": str(e)}, 503
            except Exception as e:
                return {"msg": "Permission verification failed", "error": str(e)}, 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper



def verify_side_admin_permissions_from_function(identity: str, function: Callable) -> bool:
    """Vérifie les permissions d'un administrateur de side."""
    pro_user_id = request.args.get('pro_user_id')
    return function(identity, pro_user_id)


def verify_pro_user_permissions_from_function(identity: str, function: Callable[str, str, List[str]], permissions: List[str]) -> bool:
    """Vérifie les permissions d'un utilisateur pro."""
    patient_id = request.args.get('patient_id')
    return function(identity, patient_id, permissions)


def verify_public_user_permissions_from_function(identity: str, function: Callable[str, str, List[str]], permissions: List[str]) -> bool:
    """Vérifie les permissions d'un utilisateur public."""
    patient_id = request.args.get('patient_id')
    return function(identity, patient_id, permissions)