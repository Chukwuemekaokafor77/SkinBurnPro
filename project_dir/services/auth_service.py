

import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from .database import get_user, create_user
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv('SECRET_KEY', 'aimlprojectsgroup6')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user or not verify_password(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def login(username: str, password: str):
    user = await authenticate_user(username, password)
    if not user:
        logger.error(f"Login failed for user: {username}")
        raise ValueError("Incorrect username or password")
    token = create_access_token(data={"sub": user.username})
    logger.info(f"User {username} logged in successfully")
    return token, user.id

async def register(username: str, password: str):
    existing_user = await get_user(username)
    if existing_user:
        logger.error(f"Registration failed: Username {username} already exists")
        raise ValueError("Username already exists")
    hashed_password = get_password_hash(password)
    user_id = await create_user(username, hashed_password)
    logger.info(f"User {username} registered successfully")
    return user_id

async def get_user_id_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            logger.error("Invalid token: username not found in payload")
            raise ValueError("Invalid token")
        user = await get_user(username)
        return user.id
    except jwt.PyJWTError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise ValueError("Invalid token")

async def validate_user_access(token: str, user_id: int):
    token_user_id = await get_user_id_from_token(token)
    if token_user_id != user_id:
        logger.error(f"Unauthorized access: Token user ID {token_user_id} does not match requested user ID {user_id}")
        raise ValueError("Unauthorized access")
    logger.info(f"User access validated for user ID {user_id}")