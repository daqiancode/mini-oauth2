from fastapi import APIRouter, Depends, Request,Form,Query,HTTPException
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
async def get_clients(request: Request, db: Session = Depends(get_db)):
    #order by created_at desc
    return await Clients().query()

class ClientPost(BaseModel):
    name: str
    allowed_domains: list[str]
    logo: str|None
    client_url: str|None
    description: str|None

@router.post("/clients" , description="Create client")
async def create_client(form:ClientPost):
    return await Clients().create(form.name, form.allowed_domains, form.logo, form.client_url, form.description)

@router.get("/clients/{id}" , description="Get client")
async def get_client(id:str):
    client = await Clients().get_client_by_id(id)
    if client:
        return client
    else:
        raise HTTPException(status_code=404, detail="Client not found")

class ClientPut(BaseModel):
    name: str
    allowed_domains: list[str]

@router.put("/clients/{id}" , description="Update client")
async def update_client(id:str, form:ClientPut):
    return await Clients().update(id, form.name, form.allowed_domains)

@router.delete("/clients/{id}" , description="Delete client")
async def delete_client(id:str):
    return await Clients().delete(id)
