from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    plan = Column(String, default="Free") # Free, Premium, VIP
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, index=True)
    lang = Column(String) # python, nodejs, php
    container_id = Column(String, nullable=True)
    status = Column(String, default="stopped") # running, stopped, crashed
    ram_limit_mb = Column(Integer, default=256)
    cpu_limit = Column(Float, default=0.5)
    storage_limit_mb = Column(Integer, default=500)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="projects")