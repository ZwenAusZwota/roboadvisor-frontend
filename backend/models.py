from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password = Column(String(128), nullable=False)
    
    # Relationships
    risk_profiles = relationship("RiskProfile", back_populates="user", cascade="all, delete-orphan")
    securities = relationship("Security", back_populates="user", cascade="all, delete-orphan")

class RiskProfile(Base):
    __tablename__ = "risk_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey("users.id"), nullable=True)
    risk_tolerance = Column(Integer, nullable=False)
    investment_horizon = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="risk_profiles")

class Security(Base):
    __tablename__ = "securities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    recommendation = Column(String(255), nullable=False)
    recommendation_time = Column(DateTime, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="securities")

class TelegramUser(Base):
    __tablename__ = "telegram_users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(255), nullable=False)
    language_code = Column(String(2), nullable=False)
    username = Column(String(255), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    admin = Column(Boolean, nullable=False, default=False)

