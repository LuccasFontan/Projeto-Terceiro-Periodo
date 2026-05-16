from __future__ import annotations

from typing import Any

from flask import jsonify


def success(message: str = 'OK', data: Any = None, status_code: int = 200, **extra: Any):
    payload: dict[str, Any] = {
        'success': True,
        'message': message,
        'data': data,
    }

    if isinstance(data, dict):
        payload.update(data)

    payload.update(extra)
    return jsonify(payload), status_code


def created(message: str = 'Criado com sucesso.', data: Any = None, **extra: Any):
    return success(message=message, data=data, status_code=201, **extra)


def error(message: str, status_code: int = 400, code: str | None = None, details: Any = None, **extra: Any):
    payload: dict[str, Any] = {
        'success': False,
        'message': message,
    }

    if code:
        payload['error'] = {'code': code}
        if details is not None:
            payload['error']['details'] = details
    elif details is not None:
        payload['error'] = details

    payload.update(extra)
    return jsonify(payload), status_code