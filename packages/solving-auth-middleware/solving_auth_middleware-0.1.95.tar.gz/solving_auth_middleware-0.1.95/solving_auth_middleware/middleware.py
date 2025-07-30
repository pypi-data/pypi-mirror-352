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
from typing import Optional, List, Callable

from solving_auth_middleware.enums import UserTypeEnum

def verify_permissions_from_api(identity: str, endpoint: str, token: str, permissions: List[str]) -> bool:
    """Vérifie les permissions auprès de l'API de permissions."""
    try:
        response = requests.post(
            endpoint,
            json={'identity': identity, 'permissions': permissions},
            headers={'Authorization': f'Bearer {token}'},
            timeout=current_app.config['PERMISSIONS_API_TIMEOUT']
        )
        return response.status_code == 200
    except requests.RequestException:
        return False

def verify_permissions_from_function(identity: str, function: Callable, user_type: UserTypeEnum, permissions: List[str]) -> bool:
    """Vérifie les permissions auprès de la fonction."""
    if user_type == UserTypeEnum.USER_ADMIN:
        return verify_side_admin_permissions_from_function(identity, function)
    elif user_type == UserTypeEnum.PRO:
        return verify_pro_user_permissions_from_function(identity, function)
    elif user_type == UserTypeEnum.PUBLIC:
        return verify_public_user_permissions_from_function(identity, function, permissions)
    else:
        return False

def requires_permissions(
    user_type: UserTypeEnum = UserTypeEnum.PRO,
    location: str = 'headers',
    fresh: bool = False,
    audit_fn: Optional[Callable] = None,
    verify_fn: Optional[Callable] = None,
    required_permissions: Optional[List[str]] = None,
):
    """
    Décorateur pour vérifier les permissions
    Utilise jwt_required en interne pour la validation du JWT.
    
    Args:
        user_type.value: Type d'utilisateur ('public', 'pro', 'side_admin')
        location: Emplacement du token ('header', 'cookies', 'query_string', 'json')
        fresh: Si True, exige un token frais
        audit_fn: Fonction optionnelle pour l'audit
        verify_fn: Fonction personnalisée pour la vérification des permissions
        required_permissions: Liste des permissions requises (utilisé avec verify_fn)
        jwt_manager: Instance optionnelle de JWTManager à utiliser
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required(locations=[location], fresh=fresh)
        def decorator(*args, **kwargs):
            try:
                # Récupération des informations du JWT
                jwt_data = get_jwt()
                identity = get_jwt_identity()
                current_user_type = jwt_data.get('user_type')
                if current_user_type != user_type.value:
                    return {"msg": f"Insufficient permissions for {current_user_type} user"}, 403


                token = request.headers.get('Authorization', '').split(' ')[1]
                current_app.logger.debug(f"Token: {token}")
                current_app.logger.debug(f"Identity: {identity}")
                current_app.logger.debug(f"Required permissions: {required_permissions}")
                # Vérification des permissions
                if verify_fn is not None:
                    # Vérification via fonction personnalisée
                    if user_type == UserTypeEnum.USER_ADMIN and request.args.get('pro_user_id'):
                        if not verify_fn(identity, request.args['pro_user_id']):
                            return {"msg": f"Insufficient permissions for {user_type.value} user"}, 403
                    elif user_type in [UserTypeEnum.PRO, UserTypeEnum.PUBLIC] and request.args.get('patient_id'):
                        if not verify_fn(identity, request.args['patient_id'], required_permissions or []):
                            return {"msg": f"Insufficient permissions for {user_type.value} user"}, 403
                    else:
                        if not verify_fn(identity, required_permissions or []):
                            return {"msg": f"Insufficient permissions for {user_type.value} user"}, 403
                else:
                    # Vérification via API
                    endpoint = current_app.config.get(f'{user_type.value.upper()}_USER_API_ENDPOINT')
                    current_app.logger.debug(f"User type: {user_type.value}")    
                    current_app.logger.debug(f"Endpoint: {endpoint}")
                    current_app.logger.debug(f"Token: {token}")
                    current_app.logger.debug(f"Identity: {identity}")
                    if not endpoint:
                        return {"msg": f"Invalid user type: {user_type.value}"}, 400
                    if not verify_permissions_from_api(identity, endpoint, token, required_permissions or []):
                        return {"msg": f"Insufficient permissions for {user_type.value} user"}, 403

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
    pro_user_id = request.args.get('pro_user_id', None) 
    return function(identity, pro_user_id)


def verify_pro_user_permissions_from_function(identity: str, function: Callable[str, str, List[str]], permissions: List[str]) -> bool:
    """Vérifie les permissions d'un utilisateur pro."""
    patient_id = request.args.get('patient_id', None)
    return function(identity, patient_id, permissions)


def verify_public_user_permissions_from_function(identity: str, function: Callable[str, str, List[str]], permissions: List[str]) -> bool:
    """Vérifie les permissions d'un utilisateur public."""
    patient_id = request.args.get('patient_id', None)
    return function(identity, patient_id, permissions)