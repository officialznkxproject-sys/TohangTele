from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    tenant_id = Column(Integer, ForeignKey('tenants.id'))
    
    tenant = relationship("Tenant", back_populates="users")

class Tenant(Base):
    __tablename__ = 'tenants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    prefix = Column(String(5), default='/')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, nullable=False)
    
    users = relationship("User", back_populates="tenant")
    custom_commands = relationship("CustomCommand", back_populates="tenant")

class CustomCommand(Base):
    __tablename__ = 'custom_commands'
    
    id = Column(Integer, primary_key=True)
    command = Column(String(50), nullable=False)
    response = Column(String(2000), nullable=False)
    tenant_id = Column(Integer, ForeignKey('tenants.id'))
    
    tenant = relationship("Tenant", back_populates="custom_commands")
