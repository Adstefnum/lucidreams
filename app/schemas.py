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
    text: str

class PostOutputSchema(BaseModel):
    post_id: int
    text: str
class OAuth2PasswordRequestFormEmail(BaseModel):
    email: EmailStr
    password: str