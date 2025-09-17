from app.drivers.db import db_readonly, db_transaction
from app.models.models import Client
from fastapi.exceptions import HTTPException
from app.utils.rands import rand_str
from sqlalchemy import select
from pydantic import BaseModel
from app.utils.jwts import create_key_pair


class ClientUpdate(BaseModel):
    name: str|None
    allowed_uris: list[str]|None
    logo: str|None
    client_url: str|None
    description: str|None
    jwt_expires_in_hours: int|None

class Clients:

    async def create(self, name:str, owner_user_id:str, allowed_uris:list[str]=None, logo:str=None, client_url:str=None, description:str=None , jwt_expires_in_hours:int=24, jwt_algorithm:str="EdDSA"):
        jwt_private_key, jwt_public_key = create_key_pair(jwt_algorithm)
        async with db_transaction() as session:
            client = Client(name=name, client_secret=rand_str(32), allowed_uris=allowed_uris, 
                            logo=logo, client_url=client_url, description=description, owner_user_id=owner_user_id,
                            jwt_expires_in_hours=jwt_expires_in_hours, jwt_algorithm=jwt_algorithm, jwt_public_key=jwt_public_key, jwt_private_key=jwt_private_key)
            
            session.add(client)
            return client 
       
    async def get(self, id:str):
        async with db_readonly() as session:
            stmt = select(Client).where(Client.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none() # one_or_none return Row object instead of ORM object

        
    async def update(self, id:str, form:ClientUpdate):
        async with db_transaction() as session:
            stmt = select(Client).where(Client.id == id)
            result = await session.execute(stmt)
            client = result.scalar_one_or_none() # scalar_one_or_none return ORM object instead of Row object
            if not client:
                return None
            if form.name:
                client.name = form.name
            if form.allowed_domains:
                client.allowed_domains = form.allowed_domains
            if form.logo:
                client.logo = form.logo
            if form.allowed_uris:
                client.allowed_uris = form.allowed_uris
            if form.client_url:
                client.client_url = form.client_url
            if form.description:
                client.description = form.description
            if form.jwt_expires_in_hours:
                client.jwt_expires_in_hours = form.jwt_expires_in_hours
            return client
        
    async def delete(self, id:str):
        async with db_transaction() as session:
            stmt = select(Client).where(Client.id == id)
            result = await session.execute(stmt)
            client = result.scalar_one_or_none()
            await session.delete(client)

    async def query(self, name:str=None):
        async with db_readonly() as session:
            stmt = select(Client)
            if name: # name like
                stmt = stmt.where(Client.name.like(f"%{name}%"))
            # order by created_at desc
            stmt = stmt.order_by(Client.created_at.desc())
            result = await session.execute(stmt)
            return result.scalars().all()
        
    async def reset_jwt_key(self, id:str):
        async with db_transaction() as session:
            stmt = select(Client).where(Client.id == id)
            result = await session.execute(stmt)
            client = result.scalar_one_or_none()
            if not client:
                raise HTTPException(status_code=404, detail="Client not found")
            client.jwt_private_key, client.jwt_public_key = create_key_pair(client.jwt_algorithm)
            return client
        
    async def reset_secret(self, id:str):
        async with db_transaction() as session:
            stmt = select(Client).where(Client.id == id)
            result = await session.execute(stmt)
            client = result.scalar_one_or_none()
            if not client:
                raise HTTPException(status_code=404, detail="Client not found")
            client.client_secret = rand_str(32,True)
            return client

    async def list(self, disabled: bool = None):
        async with db_readonly() as session:
            stmt = select(Client)
            if disabled is not None:
                stmt = stmt.where(Client.disabled == disabled)
            result = await session.execute(stmt)
            return result.scalars().all()