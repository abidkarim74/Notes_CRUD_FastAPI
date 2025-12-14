from schemas.auth_schemas import UserCreateSchema, UserLoginSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Response
from sqlalchemy import select
from itsdangerous import Signer
from models.auth_models import User
from utils.hash_services import hash_password_func, verify_password
from utils.token_services import generate_access_token, generate_refresh_token
import os
from utils.token_services import verify_token
from jose.exceptions import JWTError, ExpiredSignatureError


class AuthController():
    signer = Signer(os.getenv('SIGNER_KEY'))
    
    @staticmethod
    async def signup_func(data: UserCreateSchema, db: AsyncSession, res: Response):
        try:
            statement = select(User).where(User.email==data.email)
            
            result = await db.execute(statement)
                        
            user = result.scalar_one_or_none()
                        
            if user:
                raise HTTPException(status_code=400, detail='Email or username already exist!')
            
            hashed_password = hash_password_func(data.password)
            
            new_user = User(email=data.email, name=data.name,  password=hashed_password)
                        
            db.add(new_user)
            
            await db.commit()
            
            await db.refresh(new_user)
            
            access_token = generate_access_token({'id': new_user.id})
            
            refresh_token =  generate_refresh_token({'id': new_user.id})
            
            signed_refresh_token = AuthController.signer.sign(refresh_token.encode()).decode()
            
            res.set_cookie(
                key='refreshToken', 
                value=signed_refresh_token,
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age=60*60*24*7
            )
            return access_token
                                
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail='Database error!')
        
        except Exception as e:
            await db.rollback()
            error_dict = e.__dict__
            
            raise HTTPException(
                status_code=error_dict.get('status_code', 500),
                detail=error_dict.get('detail', 'Internal server error!')
            )    
    
    
    @staticmethod
    async def login_func(data: UserLoginSchema, db: AsyncSession, res: Response):
        try:
            statement1 = select(User).where(User.email==data.email)
            
            result = await db.execute(statement1)
            
            exisiting_user = result.scalar_one_or_none()
            
            if not exisiting_user:
                raise HTTPException(status_code=404, detail='User does not exist!')
            
            is_match = verify_password(data.password, exisiting_user.password)
            
            if not is_match:
                raise HTTPException(status_code=400, detail='Incorrect password!')
            
            access_token = generate_access_token({'id': exisiting_user.id})
            
            refresh_token =  generate_refresh_token({'id': exisiting_user.id})
            
            signed_refresh_token = AuthController.signer.sign(refresh_token.encode()).decode()
            
            res.set_cookie(
                key='refreshToken', 
                value=signed_refresh_token,
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age=60*60*24*7
            )
            return access_token
                
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f'Database error: {str(e)}')
        
        except Exception as e:
            await db.rollback()
            error_dict = e.__dict__
            
            raise HTTPException(
                status_code=error_dict.get('status_code', 500),
                detail=error_dict.get('detail', 'Internal server error!')
            )
        
        
    @staticmethod
    async def refresh_access_token_func(refresh: str):
        try:
            if refresh == None:
                raise HTTPException(status_code=401, detail='You are not authorized to perform this task')
            
            unsigned_refresh_token = AuthController.signer.unsign(refresh.encode()).decode()
            
            payload = verify_token(unsigned_refresh_token, 'refresh')
                        
            if payload.get('type') == 'access':
                raise HTTPException(status_code=403, detail='Invalid token type!')
            
            new_access_token = generate_access_token({'id': payload.get('id')})
                        
            return  new_access_token
           
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token has expired')
        
        except JWTError:
            raise HTTPException(status_code=403, detail='Invalid token')             
        
        except Exception as e:
            error_dict = e.__dict__
            
            raise HTTPException(
                status_code=error_dict.get('status_code', 500),
                detail=error_dict.get('detail', 'Internal server error!')
            )

    
    @staticmethod
    async def logout_user_func(res: Response):
        res.delete_cookie("refreshToken")
        return {"message": "Logged out successfully"}
        
   
        
        
  