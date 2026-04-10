from __future__ import annotations

from functools import wraps

from backend.responses import error
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def jwt_required_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('perfil') != 'administrador':
            return error('Acesso restrito ao administrador.', 403, 'FORBIDDEN')
        return fn(*args, **kwargs)

    return wrapper


def jwt_required_any(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)

    return wrapper
