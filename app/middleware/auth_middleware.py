from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from utils.token_services import verify_token
from jose.exceptions import JWTError, ExpiredSignatureError


async def verify_authentication(token: str = Depends(OAuth2PasswordBearer(tokenUrl="login"))):
    try:
        payload = verify_token(token, 'access')
        
        if payload == None:
            raise HTTPException(
                status_code=401,
                detail='You are not authorized!',
                headers={'WWW-Authenticated': 'Bearer'}
            )
        else:
            return payload   
            
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token has expired')
        
    except JWTError:
        raise HTTPException(status_code=403, detail='Invalid token') 