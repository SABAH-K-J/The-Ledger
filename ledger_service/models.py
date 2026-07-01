# ledger_service/models.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# This sets up a local database file named "ledger.db"
DATABASE_URL = "sqlite:///./ledger.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    role = Column(String)
    group_id = Column(Integer, default=1)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    
    # Status: "PENDING", "VERIFIED", "INVESTED"
    status = Column(String, default="PENDING") 
    
    # Linking this money to a User
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)