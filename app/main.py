from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from cachetools import TTLCache
import json
from . import models, schemas, auth
from .models import SessionLocal

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

cache = TTLCache(maxsize=100, ttl=300)  # Cache setup for getPosts

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for token authentication
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = auth.verify_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=schemas.TokenSchema)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/addPost", response_model=schemas.PostOutputSchema)
async def add_post(post: schemas.PostInputSchema, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_post = models.Post(**post.dict(), user_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return {"post_id": db_post.id, "text": db_post.text}

@app.get("/getPosts", response_model=List[schemas.PostOutputSchema])
async def get_posts(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cache_key = f"user_posts_{current_user.id}"
    if cache_key in cache:
        # Return cached posts
        return json.loads(cache[cache_key])
    posts = db.query(models.Post).filter(models.Post.user_id == current_user.id).all()
    cache[cache_key] = json.dumps(posts)  # Serialize posts for caching
    return posts

@app.post("/deletePost")
async def delete_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == post_id, models.Post.user_id == current_user.id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}

