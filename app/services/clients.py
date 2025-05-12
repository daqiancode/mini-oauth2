from app.drivers.db import db_readonly, db_transaction
from app.models.models import Client
from fastapi.exceptions import HTTPException
from app.utils.rands import rand_str

class Clients:

    def create(self, name:str, allowed_domains:list[str], logo:str=None, client_url:str=None, description:str=None):
        with db_transaction() as session:
            client = Client(name=name, client_secret=rand_str(32,True), allowed_domains=allowed_domains, logo=logo, client_url=client_url, description=description)
            session.add(client)
            session.flush()
            id = client.id
        return self.get_client_by_id(id)    
       
    def get_client_by_id(self, id:str):
        with db_readonly() as session:
            return session.query(Client).filter(Client.id == id).first()
        
    def update(self, id:str, name:str, allowed_domains:list[str]):
        with db_transaction() as session:
            client = session.query(Client).filter(Client.id == id).first()
            if name:
                client.name = name
            if allowed_domains:
                client.allowed_domains = allowed_domains
            return client
        
    def delete(self, id:str):
        with db_transaction() as session:
            client = session.query(Client).filter(Client.id == id).first()
            session.delete(client)

    def query(self, name:str=None):
        with db_readonly() as session:
            query = session.query(Client)
            if name: # name like
                query = query.filter(Client.name.like(f"%{name}%"))
            # order by created_at desc
            query = query.order_by(Client.created_at.desc())
            return query.all()