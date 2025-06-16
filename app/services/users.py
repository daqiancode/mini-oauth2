from app.drivers.db import db_readonly, db_transaction
from app.models.models import User, UserSource
from fastapi.exceptions import HTTPException
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# user fields except password
query_keys = [User.id, User.name, User.email, User.openid, User.role, User.avatar, User.source, User.disabled, User.created_at, User.updated_at]


class Users:
    async def signin(self, email: str, password: str):
        async with db_readonly() as session:
            result = await session.execute(select(User).filter(User.email == email))
            user = result.scalar_one_or_none()
            if not user:
                raise Exception("User not found")
            if user.disabled:
                raise Exception("User disabled")
            if not self.verify_password(password, user.password):
                raise Exception("Invalid credentials")
            return user.id
            
    async def signup(self, name: str, email: str, password: str):
        return await self.create(name, email, password)

    async def create(self, name: str, email: str, password: str, role: str = None):
        async with db_transaction() as session:
            # check email 
            result = await session.execute(select(User).filter(User.email == email))
            if result.scalar_one_or_none() is not None:
                raise HTTPException(status_code=400, detail="User already exists")
            user = User(name=name, email=email, password=self.hash_password(password), source=UserSource.local, role=role)
            session.add(user)
            await session.flush()
            user_id = user.id
        return await self.get(user_id)

    async def get_user_by_email(self, email: str):
        async with db_readonly() as session:
            result = await session.execute(select(*query_keys).filter(User.email == email))
            r = result.first()
            if r:
                return r._asdict()
            return None
        
    async def check_email_exists(self, email: str):
        async with db_readonly() as session:
            result = await session.execute(select(User).filter(User.email == email))
            return result.scalar_one_or_none() is not None

    def verify_password(self, password: str, hashed_password: str):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def hash_password(self, password: str):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    async def query(self, name: str = None, email: str = None, page: int = 1, page_size: int = 10):
        async with db_readonly() as session:
            # query without password field 
            query = select(*query_keys)
            if name:
                query = query.filter(User.name.like(f"%{name}%"))
            if email:
                query = query.filter(User.email.like(f"%{email}%"))
            # order by created_at desc
            query = query.order_by(User.created_at.desc())
            
            # Get total count
            count_result = await session.execute(select(User.id).select_from(query.subquery()))
            total = len(count_result.all())
            
            # Get paginated results
            query = query.offset((page-1)*page_size).limit(page_size)
            result = await session.execute(query)
            items = [row._asdict() for row in result.all()]
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        
    async def delete(self, id: str):
        async with db_transaction() as session:
            result = await session.execute(select(User).filter(User.id == id))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            await session.delete(user)

    async def update(self, id: str, name: str=None, email: str=None, role: str=None , disabled: bool=None, avatar: str=None):
        async with db_transaction() as session:
            result = await session.execute(select(User).filter(User.id == id))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            if name:
                user.name = name
            if email:
                user.email = email
            if role:
                user.role = role
            if disabled:
                user.disabled = disabled
            if avatar:
                user.avatar = avatar
            return user.id
        
    async def update_password(self, id: str, password: str):
        async with db_transaction() as session:
            result = await session.execute(select(User).filter(User.id == id))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user.password = self.hash_password(password)

    async def update_password_with_old_password(self, id: str, old_password: str, password: str):
        async with db_transaction() as session:
            result = await session.execute(select(User).filter(User.id == id))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            if not self.verify_password(old_password, user.password):
                raise HTTPException(status_code=400, detail="Invalid old password")
            user.password = self.hash_password(password)
            

    async def get(self, id: int) -> User:
        async with db_readonly() as session:
            result = await session.execute(select(*query_keys).filter(User.id == id))
            r = result.one_or_none()
            return User(**r._asdict()) if r else None

    async def save_or_update(self, name: str, avatar: str, email: str = None, openid: str = None, source: str = None):
        async with db_transaction() as session:
            query = select(User)
            if email:
                query = query.filter(User.email == email)
            elif openid:
                query = query.filter(User.openid == openid)
            else:
                raise HTTPException(status_code=400, detail="email or openid is required")
            
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(name=name, email=email, openid=openid, avatar=avatar, source=source)
                session.add(user)
            else:
                user.name = name
                user.avatar = avatar
                user.source = source
            return user.id
        
    async def list(self, ids: list[int]):
        async with db_readonly() as session:
            result = await session.execute(select(*query_keys).filter(User.id.in_(ids)))
            return [row._asdict() for row in result.all()]

