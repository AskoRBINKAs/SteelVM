from fastapi import APIRouter, Depends, HTTPException
from models import User
from schemas import UserLoginModel, UserRegisterModel
from database import get_db
from passlib.hash import pbkdf2_sha512
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from utils import generate_token, get_current_user

router = APIRouter(
    prefix='/api/auth',
    tags=['Auth for admins']
)


@router.post('/login/')
async def login(user_details: UserLoginModel, db:AsyncSession = Depends(get_db)):
    user = await db.execute(Select(User).where(User.email==user_details.email))
    user = user.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )
    if pbkdf2_sha512.verify(user_details.password,user.password):
        return {
            'token':await generate_token(user_details)
        }
    raise HTTPException(
        status_code=403,
        detail='Wrong password'
    )


@router.post('/register')
async def register(new_user_details: UserRegisterModel, db:AsyncSession = Depends(get_db)):
    existing_user = await db.execute(Select(User).where(User.email==new_user_details.email))
    if existing_user.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=401,
            detail="User with this email already exists"
        )
    new_user = User()
    new_user.email = new_user_details.email
    new_user.password = pbkdf2_sha512.hash(new_user_details.password)
    new_user.username = new_user_details.username
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.get('/validate-token')
async def validate_token(user = Depends(get_current_user)):
    return {'status':'ok'}