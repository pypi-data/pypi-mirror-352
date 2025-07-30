"""
Authentication utilities for agent core functionality.
"""
import asyncio
import json
from typing import Dict, Any, Optional

import httpx
from jose import jwt, JWTError
from jose.utils import base64url_decode


async def validate_token(
    token: str, 
    jwks_url: str, 
    audience: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validates a JWT token against JWKS endpoint.
    
    Args:
        token: The JWT token to validate
        jwks_url: The URL to the JWKS endpoint
        audience: Optional audience to validate against
        
    Returns:
        Dict containing the validated claims
        
    Raises:
        ValueError: If the token is invalid or cannot be verified
    """
    try:
        # Get the JWKS from the URL
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            jwks = response.json()
        
        # Parse the token header and get key ID
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise ValueError("Token doesn't have a key ID (kid)")
        
        # Find the matching key in JWKS
        key = None
        for jwk in jwks.get("keys", []):
            if jwk.get("kid") == kid:
                key = jwk
                break
        
        if not key:
            raise ValueError(f"Key ID {kid} not found in JWKS")
        
        # Verify the token
        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=audience,
            options={"verify_aud": audience is not None}
        )
        
        # Verify token hasn't expired
        if "exp" not in claims:
            raise ValueError("Token has no expiration claim")
        
        # Get the subject (user ID)
        if "sub" not in claims:
            raise ValueError("Token has no subject claim")
        
        return claims
        
    except JWTError as e:
        raise ValueError(f"JWT validation error: {str(e)}")
    except httpx.HTTPError as e:
        raise ValueError(f"Error fetching JWKS: {str(e)}")
    except Exception as e:
        raise ValueError(f"Token validation error: {str(e)}") 
    
