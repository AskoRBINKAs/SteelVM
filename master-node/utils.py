from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from schemas import UserLoginModel
import jwt
from datetime import datetime, timezone, timedelta
from models import User, HostMachine


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/ayth/login") 

async def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],db:AsyncSession=Depends(get_db)):
    try:
        data = jwt.decode(token,'secret',algorithms='HS256')
        user = await db.execute(Select(User).where(User.email==data['email']))
        return user.scalar()
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=403,
            detail='Invalid token'
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=403,
            detail='Token expired'
        )
    except:
        raise HTTPException(
            status_code=403,
            detail='Invalid token'
        )
async def get_current_host(token:Annotated[str,Depends(oauth2_scheme)],db:AsyncSession=Depends(get_db)):
    try:
        print(token)
        host = await db.execute(Select(HostMachine).where(HostMachine.access_key==token))
        host = host.scalar_one_or_none()
        if host is None:
            raise HTTPException(
                status_code=403,
                detail='Host unauthorized'
            )
        return host
    except:
        raise HTTPException(
            status_code=403,
            detail='Host unauthorized'
        )

async def generate_token(user:UserLoginModel) -> str:
    token = jwt.encode({'email':user.email,
                        "exp":datetime.now(tz=timezone.utc)+timedelta(days=7)}
                       ,'secret',algorithm="HS256")
    return token