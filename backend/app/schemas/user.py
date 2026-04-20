from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    username: str
    email: str
    full_name: str | None = None
    avatar_url: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str
    