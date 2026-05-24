from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, index=True)
    cam_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    emotion = Column(String)
    threat_level = Column(String)
    safety_score = Column(Float)
    screenshot_path = Column(String)

class EmotionLog(Base):
    __tablename__ = 'emotion_log'
    id = Column(Integer, primary_key=True, index=True)
    cam_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    emotions_json = Column(String) # JSON string
    safety_score = Column(Float)
    threat_level = Column(String)

class Incident(Base):
    __tablename__ = 'incidents'
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer)
    description = Column(String)
    screenshot_path = Column(String)
    video_clip_path = Column(String)

class CameraStatus(Base):
    __tablename__ = 'camera_status'
    id = Column(Integer, primary_key=True, index=True)
    cam_id = Column(String, unique=True, index=True)
    name = Column(String)
    url = Column(String)
    status = Column(String)
    last_active = Column(DateTime, default=datetime.utcnow)

engine = create_engine('sqlite:///../data/safeguard.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    import os
    os.makedirs('../data', exist_ok=True)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
