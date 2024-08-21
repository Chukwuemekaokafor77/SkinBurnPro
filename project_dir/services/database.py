import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Database configuration
DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '0000')
DB_HOSTNAME = os.getenv('DB_HOSTNAME', 'db')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'aimlgroup6')

DB_URL = f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}"

# Create async engine and session
engine = create_async_engine(DB_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create Base class
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

class Classification(Base):
    __tablename__ = "classifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    image_name = Column(String)
    predicted_class = Column(String)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_name": self.image_name,
            "predicted_class": self.predicted_class,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

# Create tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_user(username: str) -> User:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(User.__table__.select().where(User.username == username))
            return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error fetching user {username}: {e}")
        raise

async def create_user(username: str, hashed_password: str) -> User:
    try:
        async with AsyncSessionLocal() as session:
            db_user = User(username=username, password_hash=hashed_password)
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
            logger.info(f"User {username} created successfully")
            return db_user
    except Exception as e:
        logger.error(f"Error creating user {username}: {e}")
        await session.rollback()  # Ensure rollback in case of error
        raise

async def add_classification(user_id: int, image_name: str, predicted_class: str, confidence: float) -> Classification:
    try:
        async with AsyncSessionLocal() as session:
            db_classification = Classification(
                user_id=user_id,
                image_name=image_name,
                predicted_class=predicted_class,
                confidence=confidence
            )
            session.add(db_classification)
            await session.commit()
            await session.refresh(db_classification)
            logger.info(f"Classification for user_id {user_id} added successfully")
            return db_classification
    except Exception as e:
        logger.error(f"Error adding classification for user_id {user_id}: {e}")
        await session.rollback()
        raise

async def get_user_classifications(user_id: int) -> List[Dict]:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(Classification.__table__.select().where(Classification.user_id == user_id))
            classifications = result.fetchall()
            logger.info(f"Retrieved {len(classifications)} classifications for user_id {user_id}")
            return [Classification(**dict(row)).to_dict() for row in classifications]
    except Exception as e:
        logger.error(f"Error retrieving classifications for user_id {user_id}: {e}")
        raise
