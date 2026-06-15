from fastapi import FastAPI, HTTPException, Depends, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
from typing import Annotated, Optional
from fastapi.responses import JSONResponse

app = FastAPI(title="authentocation system  Api")

# Security
security = HTTPBearer()

# In-memory database
users = {}
members = []

# ==================== Models ====================
class UserModel(BaseModel):
    email: str
    password: str

class Api(BaseModel):
    id: str
    name: Annotated[str, Field(description="name of office employee", examples=["Usman", "Furqan"])]
    father_name: Annotated[str, Field(max_length=30)]
    age: Annotated[int, Field(gt=0, lt=100, strict=True)]
    designation: Optional[str] = None
    email: EmailStr
    profile_url: str

# ==================== Token Verification ====================
def verify(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in users:
        raise HTTPException(401, "Invalid token")
    return token

# ==================== Auth Routes ====================
@app.get("/")
def root():
    return {"status": "Api run ho gaye", "port": 8080}

@app.post("/register", tags=["Auth"])
def register(user: UserModel):
    if user.email in users:
        raise HTTPException(400, "user pehlai sai hai")
    users[user.email] = user.password
    return {
        "message": "User register hogaya hai",
        "email": user.email
    }

@app.post("/login", tags=["Auth"])
def login(user: UserModel):
    if user.email not in users:
        raise HTTPException(401, "galat email and password")
    if users[user.email] != user.password:
        raise HTTPException(401, "email or password wrong")
    return {
        "access_token": user.email,
        "token_type": "bearer"
    }

@app.get("/me", tags=["Auth"])
def get_current_user(email: str = Depends(verify)):
    return {
        "email": email,
        "authenticated": True
    }

# ==================== Management Routes ====================
@app.get("/management_team", tags=["Management"])
def get_all_members(email: str = Depends(verify)):
    return {
        "count": len(members),
        "members": members
    }

@app.get("/management_team/{member_id}", tags=["Management"])
def get_member(
    member_id: str = Path(..., description="Yahan id dalen", example="001"),
    email: str = Depends(verify)
):
    for m in members:
        if m["id"] == member_id:
            return m
    raise HTTPException(404, "Member ni hai bhai, sahi id dalo")

@app.post("/management_team", tags=["Management"])
def add_member(member: Api, email: str = Depends(verify)):
    for emp in members:
        if emp["id"] == member.id:
            raise HTTPException(400, "office employee already hai hahahaha")
    
    members.append(member.dict())
    
    return JSONResponse(
        content={
            "message": "New employee add hogaye",
            "added_employee": member.dict()
        }
    )

@app.put("/management_team/{member_id}", tags=["Management"])
def update_member(
    member_id: str = Path(..., description="Member ID jo update karni hai"),
    updated_person: Api = None,
    email: str = Depends(verify)
):
    for i, person in enumerate(members):
        if person["id"] == member_id:
            updated_fields = updated_person.model_dump(exclude_unset=True)
            person.update(updated_fields)
            members[i] = person
            
            return JSONResponse(
                content={
                    "message": "Updated successfully",
                    "data": person
                }
            )
    
    raise HTTPException(404, "Member Nahi hai Bhai")

@app.delete("/management_team/{member_id}", tags=["Management"])
def delete_member(
    member_id: str = Path(..., description="Member ID jo delete karni hai"),
    email: str = Depends(verify)
):
    global members
    
    for person in members:
        if person["id"] == member_id:
            members.remove(person)
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Deleted Successfully",
                    "deleted": person
                }
            )
    
    raise HTTPException(404, "Member Nahi hai Bhai")