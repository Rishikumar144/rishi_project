"""
Pydantic Schemas
Request/response validation models for API endpoints
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# ==================== Vehicle Schemas ====================

class VehicleCreate(BaseModel):
    """Schema for creating a new vehicle"""
    vehicle_number: str = Field(..., min_length=1, max_length=50, description="Unique vehicle number/plate")
    owner_name: str = Field(..., min_length=1, max_length=100, description="Owner's name")
    model: str = Field(..., min_length=1, max_length=100, description="Vehicle model")

class VehicleResponse(BaseModel):
    """Schema for vehicle response"""
    id: int
    vehicle_number: str
    owner_name: str
    model: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== ServiceType Schemas ====================

class ServiceTypeCreate(BaseModel):
    """Schema for creating a service type"""
    name: str = Field(..., min_length=1, max_length=100, description="Service name")
    interval_days: int = Field(..., gt=0, description="Days between services")

class ServiceTypeResponse(BaseModel):
    """Schema for service type response"""
    id: int
    name: str
    interval_days: int
    
    class Config:
        from_attributes = True

# ==================== ServiceRecord Schemas ====================

class ServiceRecordCreate(BaseModel):
    """Schema for creating a service record"""
    vehicle_id: int = Field(..., gt=0, description="Vehicle ID")
    service_type_id: int = Field(..., gt=0, description="Service type ID")
    service_date: datetime = Field(..., description="Date service was performed")
    notes: Optional[str] = Field(None, description="Additional notes")

class ServiceRecordResponse(BaseModel):
    """Schema for service record response"""
    id: int
    vehicle_id: int
    service_type_id: int
    service_date: datetime
    next_service_date: datetime
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ServiceRecordDetailResponse(BaseModel):
    """Detailed service record with related data"""
    id: int
    vehicle_id: int
    vehicle_number: str
    owner_name: str
    model: str
    service_type_id: int
    service_type_name: str
    service_date: datetime
    next_service_date: datetime
    notes: Optional[str]
    status: str  # UPCOMING, DUE, OVERDUE
    days_until_due: int  # Negative if overdue
    
    class Config:
        from_attributes = True

class ServiceHistoryResponse(BaseModel):
    """Service history for a vehicle"""
    vehicle: VehicleResponse
    service_records: List[ServiceRecordDetailResponse]