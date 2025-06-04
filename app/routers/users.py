from fastapi import APIRouter, Depends, Request, Form, Query
from pydantic import BaseModel
from app.drivers.db import get_db
from app.models.models import User
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Annotated, List
from sqlalchemy.orm import Session
from app.services.users import Users
router = APIRouter(tags=["Users"])

class UserGet(BaseModel):
    name: str = None
    email: str = None
    page: int = 1

@router.get("/users", description="Get users")
async def get_users(query: Annotated[UserGet, Query()]):
    return await Users().query(name=query.name, email=query.email, page=query.page, page_size=20)

class UserPost(BaseModel):
    name: str
    email: str
    password: str
    role: str

@router.post("/users", description="Create user")
async def create_user(user: UserPost):
    return await Users().create(user.name, user.email, user.password, user.role)

class UserBatchGet(BaseModel):
    id: list[int]

@router.get("/users/list", description="Get users in batch,split ids by comma")
async def get_user_password(ids: str):
    print('ids', ids)
    ids = ids.split(',')
    if len(ids) == 0:
        return []
    ids = [int(id) for id in ids]
    return await Users().list(ids)

class UserPut(BaseModel):
    name: str
    email: str

class UserPasswordPut(BaseModel):
    password: str

@router.put("/users/{id}/password", description="Update user password")
async def update_user_password(id: int, password: UserPasswordPut):
    await Users().update_password(id, password.password)
    return "OK"

@router.delete("/users/{id}", description="Delete user")
async def delete_user(id: int):
    await Users().delete(id)
    return "OK"

@router.put("/users/{id}", description="Update user")
async def update_user(id: int, user: UserPut):
    await Users().update(id, user.name, user.email)
    return "OK"

@router.get("/users/{id}", description="Get user")
async def get_user(id: int):
    return await Users().get(id)