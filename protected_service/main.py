from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

app = FastAPI()
security = HTTPBearer()

with open("../keys/public.pem", "rb") as f:
    PUBLIC_KEY = f.read()

# Helper: Verifies the token and returns the payload (data inside)
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return jwt.decode(credentials.credentials, PUBLIC_KEY, algorithms=["RS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")

# Endpoint 1: For any valid user
@app.get("/secure-data")
def secure_data(payload: dict = Depends(verify_token)):
    return {
        "message": f"Verified! Hello {payload['sub']}", 
        "role": payload['role'],
        "secret_data": "Standard Secret"
    }

# Endpoint 2: ADMINS ONLY
@app.get("/admin-only")
def admin_only(payload: dict = Depends(verify_token)):
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return {
        "message": "Welcome, Commander.", 
        "nuclear_codes": "1234-5678-9012"
    }