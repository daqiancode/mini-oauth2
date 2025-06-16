from app.models.base import BaseModel, BaseModelUUID,Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON

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


