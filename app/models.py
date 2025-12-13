"""
Database Models
SQLAlchemy ORM models for Vehicle, ServiceType, and ServiceRecord
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Vehicle(Base):
    """
    Vehicle table - stores vehicle information
    """
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String(50), unique=True, nullable=False, index=True)
    owner_name = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to service records
    service_records = relationship("ServiceRecord", back_populates="vehicle", cascade="all, delete-orphan")

class ServiceType(Base):
    """
    ServiceType table - defines types of services and their intervals
    """
    __tablename__ = "service_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    interval_days = Column(Integer, nullable=False)  # Days between services
    
    # Relationship to service records
    service_records = relationship("ServiceRecord", back_populates="service_type")

class ServiceRecord(Base):
    """
    ServiceRecord table - tracks individual service events
    """
    __tablename__ = "service_records"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    service_type_id = Column(Integer, ForeignKey("service_types.id"), nullable=False, index=True)
    service_date = Column(DateTime, nullable=False, index=True)
    next_service_date = Column(DateTime, nullable=False, index=True)  # Auto-calculated
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="service_records")
    service_type = relationship("ServiceType", back_populates="service_records")