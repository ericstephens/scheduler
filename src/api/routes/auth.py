from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from ..schemas.auth import UserLogin, Token
from ..middleware.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Authenticate user and return access token."""
    if not authenticate_user(user_credentials.email, user_credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_credentials.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout():
    """Logout endpoint (client should delete token)."""
    return {"message": "Successfully logged out"}

@router.get("/me")
async def read_users_me(current_user_email: str = Depends(lambda: "test@example.com")):
    """Get current user information."""
    return {"email": current_user_email}