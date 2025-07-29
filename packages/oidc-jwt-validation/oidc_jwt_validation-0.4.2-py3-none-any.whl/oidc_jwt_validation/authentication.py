from jose import jwt
from starlette.exceptions import HTTPException
from datetime import datetime
from logging import Logger
from .http_service import ServiceGet
from http import HTTPStatus

ALGORITHMS = ["RS256"]
cache_timestamp = 0
cache_jwks = None


async def get_jwks_async(service: ServiceGet, issuer: str, jwks_uri: str = "/jwks"):
    global cache_timestamp
    global cache_jwks
    timestamp = datetime.timestamp(datetime.now())
    if cache_timestamp + 86400 < timestamp:
        json_url = issuer + jwks_uri
        cache_jwks = await service.get_async(json_url)
        cache_timestamp = timestamp

    return cache_jwks


def is_scope_valid(payload: dict, scope: str):
    if payload is not None and "scope" in payload:
        scope_from_payload = str(payload["scope"])
        return scope_from_payload is not None and scope in scope_from_payload.split(" ")
    return False


class Authentication:
    def __init__(self, logger: Logger, issuer: str, service: ServiceGet, jwks_uri: str):
        self.logger = logger
        self.service = service
        self.issuer = issuer
        self.jwks_uri = jwks_uri

    async def validate_async(self, token, audience: str, scope: str):
        logger = self.logger
        try:
            logger.debug("begin authentication with: %s", token)
            unverified_header = jwt.get_unverified_header(token)
            if not unverified_header["alg"].upper() in ALGORITHMS:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED.value,
                    detail="description :wrong algorithm used",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            jwks = await get_jwks_async(self.service, self.issuer, self.jwks_uri)
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {"kty": key["kty"], "kid": key["kid"], "use": key["use"], "n": key["n"], "e": key["e"]}
            if rsa_key:
                payload = jwt.decode(token, rsa_key, algorithms=ALGORITHMS, audience=audience, issuer=self.issuer)
                if not is_scope_valid(payload, scope):
                    raise HTTPException(
                        status_code=HTTPStatus.FORBIDDEN.value,
                        detail="Insufficient scope",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                return payload
            else:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED.value,
                    detail="RSA key not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED.value,
                detail="token is expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTClaimsError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED.value,
                detail="incorrect claims, please check the audience and issuer",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            exception_message = str(e)
            logger.exception('Authentication exception : %s', exception_message)
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED.value,
                detail="Unable to parse authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
