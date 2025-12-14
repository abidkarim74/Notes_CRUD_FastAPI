from dotenv import load_dotenv # type: ignore
import os
from schemas.auth_schemas import TokenPayload
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, status


load_dotenv()

ACCESS_SECRET = os.getenv("ACCESS_SECRET")
REFRESH_SECRET = os.getenv("REFRESH_SECRET")

ACCESS_EXPIRY = int(os.getenv("ACCESS_EXPIRY", 15))  
REFRESH_EXPIRY = int(os.getenv("REFRESH_EXPIRY", 7))  

ALGORITHM = os.getenv("ALGORITHM", "HS256")


def generate_access_token(payload: TokenPayload):
    try:
        to_encode = payload.dict() if hasattr(payload, "dict") else dict(payload)

        if "id" in to_encode and isinstance(to_encode["id"], (bytes, bytearray)) is False:
            to_encode["id"] = str(to_encode["id"])

        expire_time = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRY)
        
        to_encode.update({
            "exp": expire_time,
            "type": "access"
        })

        token = jwt.encode(to_encode, ACCESS_SECRET, algorithm=ALGORITHM)
        
        return token
    
    except Exception as e:
        print("JWT ERROR:", str(e))
        raise


def generate_refresh_token(payload: TokenPayload | dict):
    to_encode = payload.dict() if hasattr(payload, "dict") else payload.copy()
    
    expire_time = datetime.utcnow() + timedelta(days=REFRESH_EXPIRY)
    
    if "id" in to_encode and isinstance(to_encode["id"], (bytes, bytearray)) is False:
            to_encode["id"] = str(to_encode["id"])
    
    to_encode.update({"exp": expire_time, "type": "refresh"})
    
    return jwt.encode(to_encode, REFRESH_SECRET, algorithm=ALGORITHM)


def verify_token(token: str, token_type: str):
    try:
        if token_type == "access":
            decoded = jwt.decode(token, ACCESS_SECRET, algorithms=[ALGORITHM])
            
        elif token_type == "refresh":
            decoded = jwt.decode(token, REFRESH_SECRET, algorithms=[ALGORITHM])
        
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token type")
        
        if decoded.get("type") != token_type:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token type mismatch")

        return decoded

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")