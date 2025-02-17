
# auth.py
import json
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from flask import request, g
from werkzeug.exceptions import HTTPException

AUTH0_DOMAIN = 'YOUR_AUTH0_DOMAIN'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'YOUR_API_AUDIENCE'

class AuthError(Exception):
    """A standardized way to communicate auth failure modes"""
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header"""
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token

def check_permissions(permission, payload):
    """Checks if the required permission exists in the JWT payload"""
    if 'permissions' not in payload:
        print("🚨 No permissions found in token!", payload)  # Debugging
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    token_permissions = [perm.strip() for perm in payload['permissions']]
    print("🔍 Token permissions:", token_permissions)  # Debugging

    if permission not in token_permissions:
        print(f"🚨 Missing permission: {permission}")  # Debugging
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)

    return True



def verify_decode_jwt(token):
    """Verifies and decodes the JWT using Auth0"""
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'n': key['n'],
                'e': key['e']
            }
    
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)

def requires_auth(permission=''):
    """Decorator to check if the request has the required permission"""
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            print("🔍 Checking Authorization Header...")
            
            try:
                token = get_token_auth_header()
                print(f"🔍 Extracted Token: {token[:20]}...")

                payload = verify_decode_jwt(token)
                print(f"✅ Token Decoded Successfully: {payload}")

                check_permissions(permission, payload)
                print(f"✅ Permission {permission} exists in token!")

            except Exception as e:
                print(f"🚨 Authorization Error: {str(e)}")
                raise e

            print("✅ Passing control to the actual route function...")
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator

