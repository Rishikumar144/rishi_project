"""
Service Routes
REST API endpoints for service types and service records
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.database import get_db
from app.services.service_logic import (
    build_service_detail_response,
    build_service_history,
    generate_csv_data
)

router = APIRouter()

# ==================== Service Type Endpoints ====================

@router.post("/types", response_model=schemas.ServiceTypeResponse, status_code=status.HTTP_201_CREATED)
def create_service_type(
    service_type: schemas.ServiceTypeCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new service type
    
    - **name**: Service name (e.g., "Oil Change", "Brake Inspection")
    - **interval_days**: Days between services
    """
    return crud.create_service_type(db, service_type)

@router.get("/types", response_model=List[schemas.ServiceTypeResponse])
def list_service_types(db: Session = Depends(get_db)):
    """Get all available service types"""
    return crud.get_service_types(db)

# ==================== Service Record Endpoints ====================

@router.post("/records", response_model=schemas.ServiceRecordResponse, status_code=status.HTTP_201_CREATED)
def create_service_record(
    service_record: schemas.ServiceRecordCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new service record
    
    The next_service_date is automatically calculated based on:
    service_date + service_type.interval_days
    
    - **vehicle_id**: ID of the vehicle
    - **service_type_id**: ID of the service type
    - **service_date**: When the service was performed
    - **notes**: Optional notes about the service
    """
    # Validate vehicle exists
    vehicle = crud.get_vehicle(db, service_record.vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {service_record.vehicle_id} not found"
        )
    
    # Validate service type exists
    service_type = crud.get_service_type(db, service_record.service_type_id)
    if not service_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service type with ID {service_record.service_type_id} not found"
        )
    
    try:
        return crud.create_service_record(db, service_record)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/records", response_model=List[schemas.ServiceRecordDetailResponse])
def list_all_service_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all service records with details and status
    """
    records = crud.get_all_service_records(db, skip=skip, limit=limit)
    return [build_service_detail_response(record, db) for record in records]

@router.get("/records/overdue", response_model=List[schemas.ServiceRecordDetailResponse])
def get_overdue_services(db: Session = Depends(get_db)):
    """
    Get all overdue service records
    Services where next_service_date < current date
    """
    records = crud.get_overdue_services(db)
    return [build_service_detail_response(record, db) for record in records]

@router.get("/records/upcoming", response_model=List[schemas.ServiceRecordDetailResponse])
def get_upcoming_services(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get upcoming services within specified days
    
    - **days**: Number of days to look ahead (default: 30)
    """
    records = crud.get_upcoming_services(db, days_ahead=days)
    return [build_service_detail_response(record, db) for record in records]

@router.get("/history/{vehicle_id}", response_model=schemas.ServiceHistoryResponse)
def get_service_history(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """
    Get complete service history for a specific vehicle
    Includes vehicle details and all service records with status
    """
    # Validate vehicle exists
    vehicle = crud.get_vehicle(db, vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )
    
    # Get service records
    records = crud.get_service_records_by_vehicle(db, vehicle_id)
    
    return build_service_history(vehicle, records, db)

@router.get("/export/csv")
def export_services_csv(db: Session = Depends(get_db)):
    """
    Export all service records as CSV
    Returns CSV file for download
    """
    records = crud.get_all_service_records(db, skip=0, limit=10000)
    csv_data = generate_csv_data(records, db)
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=service_records.csv"
        }
    )

@router.get("/export/{vehicle_id}/csv")
def export_vehicle_services_csv(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """
    Export service records for a specific vehicle as CSV
    """
    # Validate vehicle exists
    vehicle = crud.get_vehicle(db, vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )
    
    records = crud.get_service_records_by_vehicle(db, vehicle_id)
    csv_data = generate_csv_data(records, db)
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=vehicle_{vehicle_id}_services.csv"
        }
    )