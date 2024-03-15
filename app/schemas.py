from pydantic import BaseModel, Field, EmailStr

class SignupInputSchema(BaseModel):
    email: str
    password: str
class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True
class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PostInputSchema(BaseModel):
    content: str
    title: str

class PostOutputSchema(BaseModel):
    id: int
    title: str
    content: str
    class Config:
        orm_mode = True
        from_attributes = True
class OAuth2PasswordRequestFormEmail(BaseModel):
    email: EmailStr
    password: str