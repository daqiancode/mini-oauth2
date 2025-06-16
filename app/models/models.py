from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

import random
import string
def cuid():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BaseModelUUID(Base):
    __abstract__ = True
    
    id = Column(String(32), primary_key=True, index=True ,default=cuid)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now) 

class UserSource:
    google = "google"
    github = "github"
    apple = "apple"
    wechat = "wechat"
    linkedin = "linkedin"
    local = "local"

# oauth client
class Client(BaseModelUUID):
    __tablename__ = "clients"
    client_secret = Column(String(32))
    allowed_domains = Column(JSON)
    name = Column(String(100))
    disabled = Column(Boolean, default=False)
    logo = Column(String(200))
    client_url = Column(String(100))
    description = Column(String(500))
    
# oauth user
class User(BaseModel):
    __tablename__ = "users"
    name = Column(String(100))
    email = Column(String(100) , unique=True)
    openid = Column(String(100) , unique=True) # if there is not email, use openid as unique identifier
    password = Column(String(100))
    roles = Column(String(200))
    avatar = Column(String(200))
    disabled = Column(Boolean, default=False)
    source = Column(String(30)) # google, github, apple, wechat


