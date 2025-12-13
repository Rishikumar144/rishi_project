"""
CRUD Operations
Database operations for Vehicle, ServiceType, and ServiceRecord
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import List, Optional
from app import models, schemas

# ==================== Vehicle CRUD ====================

def create_vehicle(db: Session, vehicle: schemas.VehicleCreate) -> models.Vehicle:
    """Create a new vehicle"""
    db_vehicle = models.Vehicle(
        vehicle_number=vehicle.vehicle_number,
        owner_name=vehicle.owner_name,
        model=vehicle.model
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def get_vehicle(db: Session, vehicle_id: int) -> Optional[models.Vehicle]:
    """Get vehicle by ID"""
    return db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()

def get_vehicle_by_number(db: Session, vehicle_number: str) -> Optional[models.Vehicle]:
    """Get vehicle by vehicle number"""
    return db.query(models.Vehicle).filter(models.Vehicle.vehicle_number == vehicle_number).first()

def get_vehicles(db: Session, skip: int = 0, limit: int = 100) -> List[models.Vehicle]:
    """Get all vehicles with pagination"""
    return db.query(models.Vehicle).offset(skip).limit(limit).all()

def delete_vehicle(db: Session, vehicle_id: int) -> bool:
    """Delete a vehicle"""
    vehicle = get_vehicle(db, vehicle_id)
    if vehicle:
        db.delete(vehicle)
        db.commit()
        return True
    return False

# ==================== ServiceType CRUD ====================

def create_service_type(db: Session, service_type: schemas.ServiceTypeCreate) -> models.ServiceType:
    """Create a new service type"""
    db_service_type = models.ServiceType(
        name=service_type.name,
        interval_days=service_type.interval_days
    )
    db.add(db_service_type)
    db.commit()
    db.refresh(db_service_type)
    return db_service_type

def get_service_type(db: Session, service_type_id: int) -> Optional[models.ServiceType]:
    """Get service type by ID"""
    return db.query(models.ServiceType).filter(models.ServiceType.id == service_type_id).first()

def get_service_types(db: Session) -> List[models.ServiceType]:
    """Get all service types"""
    return db.query(models.ServiceType).all()

# ==================== ServiceRecord CRUD ====================

def create_service_record(db: Session, service_record: schemas.ServiceRecordCreate) -> models.ServiceRecord:
    """
    Create a new service record
    Automatically calculates next_service_date based on service_date + interval_days
    """
    # Get service type to retrieve interval_days
    service_type = get_service_type(db, service_record.service_type_id)
    if not service_type:
        raise ValueError(f"Service type {service_record.service_type_id} not found")
    
    # Calculate next service date using timedelta
    from datetime import timedelta
    next_service = service_record.service_date + timedelta(days=service_type.interval_days)
    
    db_service_record = models.ServiceRecord(
        vehicle_id=service_record.vehicle_id,
        service_type_id=service_record.service_type_id,
        service_date=service_record.service_date,
        next_service_date=next_service,
        notes=service_record.notes
    )
    db.add(db_service_record)
    db.commit()
    db.refresh(db_service_record)
    return db_service_record

def get_service_records_by_vehicle(db: Session, vehicle_id: int) -> List[models.ServiceRecord]:
    """Get all service records for a specific vehicle"""
    return db.query(models.ServiceRecord)\
        .filter(models.ServiceRecord.vehicle_id == vehicle_id)\
        .order_by(models.ServiceRecord.service_date.desc())\
        .all()

def get_all_service_records(db: Session, skip: int = 0, limit: int = 100) -> List[models.ServiceRecord]:
    """Get all service records with pagination"""
    return db.query(models.ServiceRecord)\
        .order_by(models.ServiceRecord.next_service_date.asc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_overdue_services(db: Session) -> List[models.ServiceRecord]:
    """Get all overdue service records"""
    now = datetime.utcnow()
    return db.query(models.ServiceRecord)\
        .filter(models.ServiceRecord.next_service_date < now)\
        .order_by(models.ServiceRecord.next_service_date.asc())\
        .all()

def get_upcoming_services(db: Session, days_ahead: int = 30) -> List[models.ServiceRecord]:
    """Get upcoming services within specified days"""
    from datetime import timedelta
    now = datetime.utcnow()
    future = now + timedelta(days=days_ahead)
    
    return db.query(models.ServiceRecord)\
        .filter(and_(
            models.ServiceRecord.next_service_date >= now,
            models.ServiceRecord.next_service_date <= future
        ))\
        .order_by(models.ServiceRecord.next_service_date.asc())\
        .all()