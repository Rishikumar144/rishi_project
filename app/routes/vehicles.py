"""
Vehicle Routes
REST API endpoints for vehicle management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle: schemas.VehicleCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new vehicle
    
    - **vehicle_number**: Unique vehicle number/plate (required)
    - **owner_name**: Owner's full name (required)
    - **model**: Vehicle model (required)
    """
    # Check if vehicle number already exists
    existing = crud.get_vehicle_by_number(db, vehicle.vehicle_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vehicle with number '{vehicle.vehicle_number}' already exists"
        )
    
    return crud.create_vehicle(db, vehicle)

@router.get("/", response_model=List[schemas.VehicleResponse])
def list_vehicles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all vehicles
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    return crud.get_vehicles(db, skip=skip, limit=limit)

@router.get("/{vehicle_id}", response_model=schemas.VehicleResponse)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific vehicle by ID
    """
    vehicle = crud.get_vehicle(db, vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )
    return vehicle

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a vehicle
    This will also delete all associated service records (cascade)
    """
    success = crud.delete_vehicle(db, vehicle_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )
    return None