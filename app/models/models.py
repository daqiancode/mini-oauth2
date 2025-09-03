from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime
from sqlalchemy import UniqueConstraint, ForeignKeyConstraint
Base = declarative_base()

import random
import string
def cuid():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

# class BaseModel(Base):
#     __abstract__ = True
    
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     created_at = Column(DateTime, default=datetime.now)
#     updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class BaseModelUUID(Base):
    __abstract__ = True
    
    id = Column(String(20), primary_key=True, index=True ,default=cuid)
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
    owner_user_id = Column(String(20))
    allowed_domains = Column(String(1000), comment="allowed domains, separated by comma")
    name = Column(String(100),nullable=False)
    disabled = Column(Boolean, default=False)
    logo = Column(String(200),nullable=True)
    client_url = Column(String(100),nullable=True)
    description = Column(String(500),nullable=True)
    jwt_expires_in_hours = Column(Integer , default=24)
    jwt_algorithm = Column(String(30) , default="EdDSA")
    jwt_public_key = Column(String(200), comment="jwt public key with pem format")
    jwt_private_key = Column(String(200), comment="jwt private key with pem format")

    ForeignKeyConstraint(
        ['owner_user_id'],
        ['users.id'],
        name='fk_client_owner_user',
        ondelete="CASCADE",
        onupdate="CASCADE"
    )

    
# oauth user
class User(BaseModelUUID):
    __tablename__ = "users"
    name = Column(String(100))
    email = Column(String(100) , unique=True,nullable=True)
    mobile = Column(String(100) , unique=True,nullable=True)
    openid = Column(String(100) , unique=True,nullable=True) # if there is not email, use openid as unique identifier
    password = Column(String(100),nullable=True)
    avatar = Column(String(200),nullable=True)
    disabled = Column(Boolean, default=False)
    source = Column(String(30),nullable=True) # google, github, apple, wechat


class ClientUser(BaseModelUUID):
    __tablename__ = "client_users"
    client_id = Column(String(20), ForeignKey("clients.id"), index=True)
    user_id = Column(String(20), ForeignKey("users.id"), index=True)
    roles = Column(String(200),nullable=True, comment="roles, separated by comma")
    disabled = Column(Boolean, default=False)

    # client_id & user_id are unique
    __table_args__ = (UniqueConstraint("client_id", "user_id", name="uix_client_user"),)

    ForeignKeyConstraint(
        ['client_id'],
        ['clients.id'],
        name='fk_client_user_client',
        ondelete="CASCADE",
        onupdate="CASCADE"
    )
    ForeignKeyConstraint(
        ['user_id'],
        ['users.id'],
        name='fk_client_user_user',
        ondelete="CASCADE",
        onupdate="CASCADE"
    )
