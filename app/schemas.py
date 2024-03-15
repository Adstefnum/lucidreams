from pydantic import BaseModel, Field

class SignupInputSchema(BaseModel):
    email: str
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PostInputSchema(BaseModel):
    text: str

class PostOutputSchema(BaseModel):
    post_id: int
    text: str
