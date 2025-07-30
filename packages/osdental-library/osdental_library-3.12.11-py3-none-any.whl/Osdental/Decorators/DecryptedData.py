import inspect
from functools import wraps
from typing import Callable
from graphql import GraphQLResolveInfo
from Osdental.Encryptor.Jwt import JWT
from Osdental.Exception.ControlledException import UnauthorizedException
from Osdental.Handlers.DBSecurityQuery import DBSecurityQuery
from Osdental.Handlers.Instances import jwt_user_key, aes
from Osdental.Models.Token import AuthToken
from Osdental.Shared.Message import Message
from Osdental.Shared.Constant import Constant

db_security_query = DBSecurityQuery()

def process_encrypted_data():
    def decorator(func:Callable):
        @wraps(func)
        async def wrapper(self, info:GraphQLResolveInfo = None, aes_data:str = None, **rest_kwargs): 
            legacy = await db_security_query.get_legacy_data()
            token = None
            user_token_encrypted = info.context['user_token']
            if user_token_encrypted:
                user_token = aes.decrypt(legacy.aes_key_user, user_token_encrypted)
                token = AuthToken.from_jwt(JWT.extract_payload(user_token, jwt_user_key), legacy, jwt_user_key)
                is_auth = await db_security_query.validate_auth_token(token.id_token, token.id_user)
                if not is_auth:
                    raise UnauthorizedException(message=Message.PORTAL_ACCESS_RESTRICTED_MSG, error=Message.PORTAL_ACCESS_RESTRICTED_MSG)

            data = None
            if aes_data:
                decrypted_data = aes.decrypt(legacy.aes_key_auth, aes_data)
                data = decrypted_data

            headers = info.context.get('headers')
            if headers and token.abbreviation.startswith(Constant.PROFILE_MARKETING):
                id_external_mk = headers.get('idExternalEnterpriseMk')
                if id_external_mk:
                    token.id_external_enterprise = aes.decrypt(token.aes_key_auth, id_external_mk)

            sig = inspect.signature(func)
            kwargs_to_pass = {}
            if 'token' in sig.parameters:
                kwargs_to_pass['token'] = token
            if 'data' in sig.parameters:
                kwargs_to_pass['data'] = data

            return await func(self, **kwargs_to_pass, **rest_kwargs)
        
        return wrapper
    return decorator