from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError, ExpiredSignatureError

from exceptions import TokenExpiredError, InvalidTokenError
from security.interfaces import JWTAuthManagerInterface


class JWTAuthManager(JWTAuthManagerInterface):
    """
    A manager for creating, decoding, and verifying JWT access and refresh tokens.
    """

    _ACCESS_KEY_TIMEDELTA_MINUTES = 60
    _REFRESH_KEY_TIMEDELTA_MINUTES = 60 * 24 * 7

    def __init__(self, secret_key_access: str, secret_key_refresh: str, algorithm: str):
        """
        Initializes the JWTAuthManager with separate secret keys for access and refresh tokens and specifies the JWT algorithm to use.
        
        Args:
            secret_key_access: Secret key for signing access tokens.
            secret_key_refresh: Secret key for signing refresh tokens.
            algorithm: The JWT algorithm to use for encoding and decoding tokens.
        """
        self._secret_key_access = secret_key_access
        self._secret_key_refresh = secret_key_refresh
        self._algorithm = algorithm

    def _create_token(self, data: dict, secret_key: str, expires_delta: timedelta) -> str:
        """
        Creates a JWT token containing the provided data and an expiration timestamp.
        
        Args:
            data: The payload to include in the token.
            secret_key: The secret key used to sign the token.
            expires_delta: The time duration after which the token expires.
        
        Returns:
            The encoded JWT token as a string.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, secret_key, algorithm=self._algorithm)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Generates a JWT access token containing the provided data and an expiration time.
        
        If no expiration is specified, the token expires in 60 minutes by default.
        
        Args:
            data: The payload to include in the token.
            expires_delta: Optional custom expiration as a timedelta.
        
        Returns:
            A JWT access token as a string.
        """
        return self._create_token(
            data,
            self._secret_key_access,
            expires_delta or timedelta(minutes=self._ACCESS_KEY_TIMEDELTA_MINUTES))

    def create_refresh_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Generates a new JWT refresh token with an optional custom expiration time.
        
        If no expiration is provided, the token defaults to a 7-day validity period.
        """
        return self._create_token(
            data,
            self._secret_key_refresh,
            expires_delta or timedelta(minutes=self._REFRESH_KEY_TIMEDELTA_MINUTES))

    def decode_access_token(self, token: str) -> dict:
        """
        Decodes and validates an access token, returning its payload as a dictionary.
        
        Raises:
            TokenExpiredError: If the token has expired.
            InvalidTokenError: If the token is invalid for any other reason.
        """
        try:
            return jwt.decode(token, self._secret_key_access, algorithms=[self._algorithm])
        except ExpiredSignatureError:
            raise TokenExpiredError
        except JWTError:
            raise InvalidTokenError

    def decode_refresh_token(self, token: str) -> dict:
        """
        Decodes and validates a refresh token, returning its payload as a dictionary.
        
        Raises:
            TokenExpiredError: If the token has expired.
            InvalidTokenError: If the token is invalid for any other reason.
        """
        try:
            return jwt.decode(token, self._secret_key_refresh, algorithms=[self._algorithm])
        except ExpiredSignatureError:
            raise TokenExpiredError
        except JWTError:
            raise InvalidTokenError

    def verify_refresh_token_or_raise(self, token: str) -> None:
        """
        Verifies the validity of a refresh token, raising an error if it is invalid or expired.
        
        Any exceptions encountered during decoding, such as token expiration or invalidity, are propagated to the caller.
        """
        self.decode_refresh_token(token)

    def verify_access_token_or_raise(self, token: str) -> None:
        """
        Verifies the validity of an access token, raising an error if the token is invalid or expired.
        
        Raises:
            TokenExpiredError: If the access token has expired.
            InvalidTokenError: If the access token is invalid for any other reason.
        """
        self.decode_access_token(token)
