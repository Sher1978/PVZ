import hmac
import hashlib
from urllib.parse import parse_qsl, unquote
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.config import settings

security = HTTPBearer()

def verify_telegram_init_data(init_data_raw: str, bot_token: str) -> dict:
    """
    Validates Telegram WebApp initData HMAC-SHA256 signature
    """
    try:
        parsed_data = dict(parse_qsl(init_data_raw, keep_blank_values=True))
        if "hash" not in parsed_data:
            raise ValueError("Hash parameter is missing in initData")
        
        hash_to_check = parsed_data.pop("hash")
        
        # Sort keys alphabetically
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        
        # Secret key calculation
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if calculated_hash != hash_to_check:
            raise ValueError("Data verification failed: Hash mismatch")
            
        return parsed_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Telegram initData authentication: {str(e)}"
        )
