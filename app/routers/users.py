from fastapi import APIRouter, Depends, Request,Form,Query
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
    name:str=None
    email:str=None
    page:int=1

@router.get("/users" , description="Get users")
def get_users(query:Annotated[UserGet, Query()]):
    return Users().query(name=query.name, email=query.email, page=query.page, page_size=20)
    
class UserPost(BaseModel):
    name:str
    email:str
    password:str
    role:str

@router.post("/users" , description="Create user")
def create_user(user:UserPost):
    return Users().create(user.name, user.email, user.password, user.role)


class UserBatchGet(BaseModel):
    id:list[int]

@router.get("/users/list" , description="Get users in batch,split ids by comma")
def get_user_password(ids:str):
    print('ids', ids)
    ids = ids.split(',')
    if len(ids) == 0:
        return []
    ids = [int(id) for id in ids]
    return Users().list(ids)

class UserPut(BaseModel):
    name:str
    email:str

class UserPasswordPut(BaseModel):
    password:str

@router.put("/users/{id}/password" , description="Update user password")
def update_user_password(id:str, password:UserPasswordPut):
    Users().update_password(id, password.password)
    return "OK"




@router.delete("/users/{id}" , description="Delete user")
def delete_user(id:str):
    Users().delete(id)
    return "OK"

@router.put("/users/{id}" , description="Update user")
def update_user(id:str, user:UserPut):
    Users().update(id, user.name, user.email)
    return "OK"

@router.get("/users/{id}" , description="Get user")
def get_user(id:str):
    return Users().get(id)