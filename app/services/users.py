from app.drivers.db import db_readonly, db_transaction
from app.models.models import User, UserSource
from fastapi.exceptions import HTTPException
import bcrypt



query_keys = [User.id, User.name, User.email,User.openid,User.role,User.avatar, User.source, User.disabled, User.created_at, User.updated_at]

class Users:

    def signin(self, email: str, password: str):
        with db_readonly() as session:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                raise Exception("User not found")
            if not self.verify_password(password, user.password):
                raise Exception("Invalid credentials")
            return user.id
            
    def signup(self, name:str, email: str, password: str):
        self.create(name, email, password, )

    def create(self, name:str, email: str, password: str, role:str=None):
        with db_transaction() as session:
            # check email 
            if session.query(User).filter(User.email == email).first() is not None:
                raise HTTPException(status_code=400, detail="User already exists")
            user = User(name=name, email=email, password=self.hash_password(password), source=UserSource.local, role=role)
            session.add(user)
            session.flush()
            user_id = user.id
        return self.get(user_id)

    def get_user_by_email(self, email: str):
        with db_readonly() as session:
            r = session.query(*query_keys).filter(User.email == email).first()
            if r:
                return r._asdict()
            return None
        
    def check_email_exists(self, email: str):
        with db_readonly() as session:
            return session.query(User).filter(User.email == email).first() is not None

    def verify_password(self, password: str, hashed_password: str):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def hash_password(self, password: str):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def query(self, name:str=None ,email:str=None, page:int=1, page_size:int=10):
        with db_readonly() as session:
            # query without password field 
            # Select all fields except password
            query = session.query(User).with_entities(User.id, User.name, User.email, User.created_at, User.updated_at)
            if name:
                query = query.filter(User.name.like(f"%{name}%"))
            if email:
                query = query.filter(User.email.like(f"%{email}%"))
            # order by created_at desc
            query = query.order_by(User.created_at.desc())
            rs = query.offset((page-1)*page_size).limit(page_size).all()
            # to dict
            items = [row._asdict() for row in rs]
            return {
                "items": items,
                "total": query.count(),
                "page": page,
                "page_size": page_size
            }
        
    def delete(self, id:str):
        with db_transaction() as session:
            user = session.query(User).filter(User.id == id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            session.delete(user)

    def update(self, id:str, name:str, email:str):
        with db_transaction() as session:
            user = session.query(User).filter(User.id == id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            if name:
                user.name = name
            if email:
                user.email = email
        
    def update_password(self, id:str, password:str):
        with db_transaction() as session:
            user = session.query(User).filter(User.id == id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user.password = self.hash_password(password)

    
    def get(self, id:str)->User:
        with db_readonly() as session:
            # query without password field 
            # Select all fields except password
            query = session.query(*query_keys)
            return query.filter(User.id == id).first()


    def save_or_update(self, name:str, avatar:str,email:str=None, openid:str=None , source:str=None):
        with db_transaction() as session:
            query = session.query(User)
            if email:
                query = query.filter(User.email == email)
            elif openid:
                query = query.filter(User.openid == openid)
            else:
                raise HTTPException(status_code=400, detail="email or openid is required")
            user = query.first()
            if not user:
                user = User(name=name, email=email, openid=openid , avatar=avatar, source=source)
                session.add(user)
            else:
                user.name = name
                user.avatar = avatar
                user.source = source
            return user.id
        
    def list(self, ids:list[int]):
        with db_readonly() as session:
            rs= session.query(*query_keys).filter(User.id.in_(ids)).all()
            return [row._asdict() for row in rs]



if __name__ == "__main__":
    print(Users().signup('test',"test1@test.com", "test"))