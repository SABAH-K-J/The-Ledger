from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from models import Base, engine, User, Transaction 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel

# --- 1. DATABASE SETUP (Must come first!) ---
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 2. SECURITY SETUP ---
security = HTTPBearer()

with open("../keys/public.pem", "rb") as f:
    PUBLIC_KEY = f.read()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        username = payload.get("sub")
        
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")

class DepositRequest(BaseModel):
    amount: int

# --- 3. APP SETUP ---
app = FastAPI()

# The Startup Script (Runs once when you turn the server on)
@app.on_event("startup")
def startup_populate_db():
    db = SessionLocal()
    
    # Check if we already have users (so we don't add them twice)
    if db.query(User).count() == 0:
        print("🌱 Seeding Database with Users...")
        
        bob = User(username="bob", role="member", group_id=1)
        alice = User(username="alice", role="head", group_id=1)
        charlie = User(username="charlie", role="admin", group_id=0)
        db.add_all([bob, alice, charlie])
        db.commit()
        print("✅ Users Created!")
    
    db.close()

@app.get("/")
def read_root():
    return {"message": "Ledger Service is Online"}

@app.post("/deposit")
def create_deposit(request: DepositRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Create a new Transaction with status "PENDING"
    new_transaction = Transaction(
        amount=request.amount,
        status="PENDING",
        owner_id=current_user.id
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return {"message": "Deposit created", "transaction_id": new_transaction.id}

# Endpoint 1: View Pending Approvals
@app.get("/approvals")
def get_pending_approvals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Security Check: Are you a Head?
    if current_user.role != "head":
        raise HTTPException(status_code=403, detail="Only Heads can access this.")
    
    # 2. Database Query: Find PENDING transactions belonging to THIS Head's group
    # We join the User table so we can filter by the owner's group_id
    # We tell it: Join User specifically where Transaction.owner_id matches User.id
    pending_txs = db.query(Transaction).join(User, Transaction.owner_id == User.id).filter(
        Transaction.status == "PENDING",
        User.group_id == current_user.group_id
    ).all()
    
    return pending_txs

# Endpoint 2: Verify a Transaction
@app.post("/verify/{transaction_id}")
def verify_transaction(transaction_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Security Check
    if current_user.role != "head":
        raise HTTPException(status_code=403, detail="Only Heads can verify.")
    
    # 2. Find the transaction
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    # 3. Verify Logic: Change status and sign it
    tx.status = "VERIFIED"
    tx.verified_by = current_user.id  # Alice signs her name
    
    db.commit()
    return {"message": f"Transaction {transaction_id} verified by {current_user.username}"}