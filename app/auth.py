import json
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from flask import request, g
from werkzeug.exceptions import HTTPException
import requests 
import socket
import os
from dotenv import load_dotenv  

load_dotenv()

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
ALGORITHMS = ['RS256']
API_AUDIENCE = os.getenv('API_AUDIENCE')


JWKS_CACHE = {}  # Store JWKS keys in memory to prevent constant network requests


def test_connection():
    """Test if Flask can reach Auth0"""
    try:
        host = "your_auth0_domain"  # Replace this with the actual domain
        port = 443  # HTTPS port
        socket.create_connection((host, port), timeout=5)
        print("✅ Flask can connect to Auth0!")
    except Exception as e:
        print(f"🚨 Flask CANNOT connect to Auth0: {e}")


class AuthError(Exception):
    """A standardized way to communicate auth failure modes"""
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def fetch_jwks_keys():
    """Fetch JWKS keys from Auth0 (caching enabled to prevent timeouts)"""
    global JWKS_CACHE
    if not JWKS_CACHE:  # Only fetch if cache is empty
        print("🔍 Fetching JWKS keys from Auth0...")

        test_connection()  # Test network connectivity before making request

        try:
            response = requests.get(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json', timeout=5)
            response.raise_for_status()
            JWKS_CACHE = response.json()
            print("✅ Successfully fetched JWKS keys from Auth0")
        except requests.exceptions.RequestException as e:
            print(f"🚨 Failed to fetch JWKS keys: {e}")
            raise AuthError({
                'code': 'jwks_fetch_failed',
                'description': 'Failed to fetch JWKS keys from Auth0'
            }, 500)
    return JWKS_CACHE


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
    print("🔍 Fetching JWKS keys from Auth0...")  # Debugging

    try:
        jwks = fetch_jwks_keys()
    except Exception as e:
        print(f"🚨 Failed to fetch JWKS keys: {str(e)}")  # Debugging
        raise AuthError({
            'code': 'jwks_fetch_failed',
            'description': 'Failed to fetch JWKS keys from Auth0'
        }, 500)

    print("🔍 Extracting unverified JWT header...")  # Debugging
    unverified_header = jwt.get_unverified_header(token)
    
    if 'kid' not in unverified_header:
        print("🚨 Invalid token: No 'kid' found")  # Debugging
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    rsa_key = {}
    print("🔍 Searching for matching JWKS key...")  # Debugging
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
            print("🔍 Decoding JWT with found JWKS key...")  # Debugging
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                audience=API_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )
            print(f"✅ Token Decoded Successfully: {payload}")  # Debugging
            return payload

        except jwt.ExpiredSignatureError:
            print("🚨 Token Expired")  # Debugging
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            print("🚨 Invalid Token Claims")  # Debugging
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Check the audience and issuer.'
            }, 401)

        except Exception as e:
            print(f"🚨 Token verification failed: {str(e)}")  # Debugging
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)

    print("🚨 Unable to find the appropriate JWKS key")  # Debugging
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