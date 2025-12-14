from fastapi import APIRouter, Depends, Response, Cookie, Request
from database.db import connect_db
from schemas.auth_schemas import UserCreateSchema, UserLoginSchema
from sqlalchemy.ext.asyncio import AsyncSession
from controllers.auth_controllers import AuthController
from middleware.auth_middleware import verify_authentication
from dependencies.rate_limit import rate_limit_20_per_minute


auth_router = APIRouter(
    prefix='/api/auth',
    tags=['Authentication']
)


@auth_router.post('/signup', status_code=201)
async def signup_route(request: Request, res: Response, data: UserCreateSchema, _=Depends(rate_limit_20_per_minute), db: AsyncSession = Depends(connect_db)):
    """
    Create a new user account.
    
    - Sets refresh token as HTTP-only cookie
    - Returns access token in response body (to be stored in client state)
    """
    return await AuthController.signup_func(data, db, res)


@auth_router.post('/login')
async def login_route(request: Request, res: Response, data: UserLoginSchema, _ = Depends(rate_limit_20_per_minute), db: AsyncSession = Depends(connect_db)):
    """
    Authenticate user with email and password.
    
    - Sets refresh token as HTTP-only cookie
    - Returns access token in response body (to be stored in client state)
    """
    return await AuthController.login_func(data, db, res)

    
@auth_router.post('/refresh-access-token')
async def refresh_token_route(refreshToken: str = Cookie(None)):
    """
    Get a new access token using refresh token.
    
    - Requires refresh token from HTTP-only cookie
    - Returns new access token in response body
    """
    return await AuthController.refresh_access_token_func(refreshToken)
  
  
@auth_router.post('/logout')
async def logout_route(res: Response, payload = Depends(verify_authentication)):
    """
    Logout user and clear authentication tokens.
    
    - Clears refresh token cookie
    - Requires valid access token in Authorization header
    """
    return await AuthController.logout_user_func(res)