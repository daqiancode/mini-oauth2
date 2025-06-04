from app.drivers.db import db_readonly, db_transaction
from app.models.models import Client
from fastapi.exceptions import HTTPException
from app.utils.rands import rand_str
from sqlalchemy import select

class Clients:

    async def create(self, name:str, allowed_domains:list[str], logo:str=None, client_url:str=None, description:str=None):
        async with db_transaction() as session:
            client = Client(name=name, client_secret=rand_str(32,True), allowed_domains=allowed_domains, logo=logo, client_url=client_url, description=description)
            session.add(client)
            return client 
       
    async def get_client_by_id(self, id:str):
        async with db_readonly() as session:
            stmt = select(Client).where(Client.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none() # one_or_none return Row object instead of ORM object

        
    async def update(self, id:str, name:str, allowed_domains:list[str]):
        async with db_transaction() as session:
            stmt = select(Client).where(Client.id == id)
            result = await session.execute(stmt)
            client = result.scalar_one_or_none() # scalar_one_or_none return ORM object instead of Row object
            if not client:
                return None
            if name:
                client.name = name
            if allowed_domains:
                client.allowed_domains = allowed_domains
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