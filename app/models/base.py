from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, DateTime, String
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