from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional


class JWTAuthManagerInterface(ABC):
    """
    Interface for JWT Authentication Manager.
    Defines methods for creating, decoding, and verifying JWT tokens.
    """

    @abstractmethod
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Generates a new JWT access token containing the provided data and optional expiration.
        
        Args:
        	data: The payload to include in the token.
        	expires_delta: Optional duration specifying the token's validity period.
        
        Returns:
        	A JWT access token as a string.
        """
        pass

    @abstractmethod
    def create_refresh_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Creates a new refresh token containing the provided data and optional expiration.
        
        Args:
            data: The payload to include in the refresh token.
            expires_delta: Optional expiration time for the token.
        
        Returns:
            A JWT refresh token as a string.
        """
        pass

    @abstractmethod
    def decode_access_token(self, token: str) -> dict:
        """
        Decodes and validates a JWT access token.
        
        Args:
            token: The JWT access token to decode.
        
        Returns:
            The payload of the access token as a dictionary.
        """
        pass

    @abstractmethod
    def decode_refresh_token(self, token: str) -> dict:
        """
        Decodes and validates a refresh token, returning its payload as a dictionary.
        
        Args:
            token: The JWT refresh token to decode.
        
        Returns:
            The decoded payload of the refresh token as a dictionary.
        """
        pass

    @abstractmethod
    def verify_refresh_token_or_raise(self, token: str) -> None:
        """
        Verifies the validity of a refresh token, raising an error if the token is invalid.
        
        Args:
            token: The refresh token to verify.
        
        Raises:
            An implementation-defined exception if the token is invalid.
        """
        pass

    @abstractmethod
    def verify_access_token_or_raise(self, token: str) -> None:
        """
        Verifies the validity of an access token, raising an error if the token is invalid.
        """
        pass
