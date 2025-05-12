from fastapi import APIRouter, Depends, Request,Form,Query
from pydantic import BaseModel
from app.drivers.db import get_db
from app.models.models import Client
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Annotated
import json
from sqlalchemy.orm import Session
from app.services.clients import Clients
router = APIRouter(tags=["Clients"])

@router.get("/clients" , description="Get clients")
def get_clients(request: Request, db: Session = Depends(get_db)):
    #order by created_at desc
    return Clients().query()

class ClientPost(BaseModel):
    name: str
    allowed_domains: list[str]
    logo: str|None
    client_url: str|None
    description: str|None

@router.post("/clients" , description="Create client")
def create_client(form:ClientPost):
    return Clients().create(form.name, form.allowed_domains, form.logo, form.client_url, form.description)


@router.get("/clients/{id}" , description="Get client")
def get_client(id:str):
    return Clients().get_client_by_id(id)

class ClientPut(BaseModel):
    name: str
    allowed_domains: list[str]

@router.put("/clients/{id}" , description="Update client")
def update_client(id:str, form:ClientPut):
    return Clients().update(id, form.name, form.allowed_domains)


@router.delete("/clients/{id}" , description="Delete client")
def delete_client(id:str):
    return Clients().delete(id)
