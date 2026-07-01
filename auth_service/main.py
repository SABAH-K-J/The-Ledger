from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from jose import jwt
from sqlalchemy.orm import Session, sessionmaker
from passlib.context import CryptContext
from models import Base, engine, User

app = FastAPI()

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

with open("../keys/private.pem", "rb") as f:
    PRIVATE_KEY = f.read()

# We don't technically need the Public Key here (only for verification)
with open("../keys/public.pem", "rb") as f:
    PUBLIC_KEY = f.read()

class UserLogin(BaseModel):
    username: str
    password: str

@app.on_event("startup")
def startup_populate_db():
    db = SessionLocal()
    if db.query(User).count() == 0:
        print("🌱 Seeding Auth Database with Users...")
        users = [
            User(username="johndoe", password_hash=pwd_context.hash("password123"), role="admin"),
            User(username="bob", password_hash=pwd_context.hash("bob123"), role="member"),
            User(username="alice", password_hash=pwd_context.hash("alice123"), role="head"),
            User(username="charlie", password_hash=pwd_context.hash("charlie123"), role="admin")
        ]
        db.add_all(users)
        db.commit()
        print("✅ Users Created!")
    db.close()

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user and pwd_context.verify(user.password, db_user.password_hash):
        payload = { 
            "sub": db_user.username, 
            "role": db_user.role 
        }
        token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
        return {"access_token": token, "token_type": "bearer"}
    else:
        return {"status": "failure", "message": "Invalid credentials"}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Auth Service"}