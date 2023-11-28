# -*- coding: utf-8 -*-
from jwt_utils.jwt_validator import jwt_validator
from rest_framework import authentication
from rest_framework import exceptions
from users.models import Token
from functools import wraps


class JwtTokensAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token_id = request.headers.get("Authorization", "")
        try:
            payload = jwt_validator(token_id)
            Token.objects.get(access_token=token_id, is_expired=0)
            request.jwt_payload = payload 
            
            return payload, None
        except Exception:
            raise exceptions.AuthenticationFailed(
                detail={"code": 401, "message": "Expired or Invalid Token"}
            )


def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            jwt_payload = getattr(request, "jwt_payload", None)
            
            if jwt_payload and (jwt_payload.get("role") == required_role or jwt_payload.get("role") == "admin" or jwt_payload.get("role") == "ADGP"):
                return view_func(self, request, *args, **kwargs)
            else:
                raise exceptions.PermissionDenied(
                    detail={"code": 403, "message": "Insufficient permissions"}
                )
        return wrapper
    return decorator
