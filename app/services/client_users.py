from app.drivers.db import db_transaction, db_readonly
from app.models.models import ClientUser,User,Client
from fastapi.exceptions import HTTPException
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import List, Tuple

class ClientUserPost(BaseModel):
    client_id: str
    email: str|None = None
    mobile: str|None = None
    openid: str|None = None
    name: str|None = None
    avatar: str|None = None
    provider: str|None = None
    # roles: str|None = None
    # disabled: bool|None = None

    

class QueryFilters(BaseModel):
    client_id: str|None = None
    user_id: str|None = None
    roles: str|None = None
    email: str|None = None
    openid: str|None = None
    mobile: str|None = None
    name: str|None = None
    disabled: bool|None = None
    page: int = 1
    page_size: int = 20


class ClientUsers:
    async def save_or_update(self, form:ClientUserPost):
        async with db_transaction() as session:
            # check client
            query = select(Client).where(Client.id == form.client_id)
            result = await session.execute(query)
            client = result.scalar_one_or_none()
            if not client:
                raise HTTPException(status_code=400, detail="Client not found")
            
            query = select(User)
            if form.email:
                query = query.filter(User.email == form.email)
            elif form.openid:
                query = query.filter(User.openid == form.openid)
            elif form.mobile:
                query = query.filter(User.mobile == form.mobile)
            else:
                raise HTTPException(status_code=400, detail="email or openid or mobile is required")
            
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(name=form.name, email=form.email,mobile=form.mobile, openid=form.openid, avatar=form.avatar, provider=form.provider)
                session.add(user)
            else:
                user.name = form.name
                user.avatar = form.avatar
                user.provider = form.provider

            # check client user
            query = select(ClientUser).where(ClientUser.client_id == form.client_id, ClientUser.user_id == user.id)
            result = await session.execute(query)
            client_user = result.scalar_one_or_none()
            if not client_user:
                client_user = ClientUser(client_id=form.client_id, user_id=user.id)
                session.add(client_user)
            # else:
            #     client_user.roles = form.roles
            #     client_user.disabled = False
            return client_user
        
    async def get_user_info(self ,user_id:str, client_id:str)->dict:
        async with db_readonly() as session:
            query = select(ClientUser).where(ClientUser.user_id == user_id, ClientUser.client_id == client_id)
            result = await session.execute(query)
            client_user = result.scalar_one_or_none()
            if not client_user:
                raise HTTPException(status_code=400, detail="Client user not found")
            query = select(User).where(User.id == client_user.user_id)
            result = await session.execute(query)
            user= result.scalar_one_or_none()
            user_dict = user.__dict__
            user_dict["client_id"] = client_user.client_id
            user_dict["roles"] = client_user.roles
            user_dict["disabled"] = client_user.disabled
            user_dict["created_at"] = client_user.created_at
            user_dict["updated_at"] = client_user.updated_at
            return user_dict
            
        
    async def get(self ,client_user_id:str):
        async with db_readonly() as session:
            query = select(ClientUser).where(ClientUser.id == client_user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        
    async def delete(self ,client_user_id:str):
        async with db_transaction() as session:
            query = select(ClientUser).where(ClientUser.id == client_user_id)
            result = await session.execute(query)
            client_user = result.scalar_one_or_none()
            if not client_user:
                raise HTTPException(status_code=400, detail="Client user not found")
            await session.delete(client_user)


    async def query(self, filters: QueryFilters) -> Tuple[List[dict], int]:
        """
        Query client users with specified filters and pagination.
        Returns a tuple of (client_users_list, total_count)
        """
        async with db_readonly() as session:
            # Build the base query with proper join
            base_query = select(ClientUser, User).join(User, ClientUser.user_id == User.id)
            
            # Apply filters
            if filters.client_id:
                base_query = base_query.where(ClientUser.client_id == filters.client_id)
            if filters.user_id:
                base_query = base_query.where(ClientUser.user_id == filters.user_id)
            if filters.roles:
                base_query = base_query.where(ClientUser.roles == filters.roles)
            if filters.email:
                base_query = base_query.where(User.email == filters.email)
            if filters.openid:
                base_query = base_query.where(User.openid == filters.openid)
            if filters.mobile:
                base_query = base_query.where(User.mobile == filters.mobile)
            if filters.name:
                base_query = base_query.where(User.name.like(f"%{filters.name}%"))
            count_query = select(func.count(ClientUser.id)).select_from(base_query.subquery())
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            print("total", total)
            
            
            # Apply ordering and pagination
            base_query = base_query.order_by(ClientUser.created_at.desc())
            base_query = base_query.offset((filters.page - 1) * filters.page_size).limit(filters.page_size)
            
            # Execute the main query
            result = await session.execute(base_query)
            rows = result.all()
            
            # Convert to list of dictionaries with combined data
            client_users = []
            for client_user, user in rows:
                user_data = {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "mobile": user.mobile,
                    "openid": user.openid,
                    "avatar": user.avatar,
                    "source": user.source,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                    "client_user_id": client_user.id,
                    "client_id": client_user.client_id,
                    "roles": client_user.roles,
                    "disabled": client_user.disabled,
                    "client_user_created_at": client_user.created_at,
                    "client_user_updated_at": client_user.updated_at
                }
                client_users.append(user_data)
            
            return client_users, 10

