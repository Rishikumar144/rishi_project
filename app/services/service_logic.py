"""
Business Logic Layer
Handles service status calculation and data transformation
"""
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from app import models, schemas

def calculate_service_status(next_service_date: datetime) -> tuple[str, int]:
    """
    Calculate service status based on next service date
    Returns: (status, days_until_due)
    
    Status values:
    - OVERDUE: next_service_date is in the past
    - DUE: next_service_date is today or within 7 days
    - UPCOMING: next_service_date is more than 7 days away
    """
    now = datetime.utcnow()
    days_until_due = (next_service_date - now).days
    
    if days_until_due < 0:
        return "OVERDUE", days_until_due
    elif days_until_due <= 7:
        return "DUE", days_until_due
    else:
        return "UPCOMING", days_until_due

def build_service_detail_response(
    service_record: models.ServiceRecord,
    db: Session
) -> schemas.ServiceRecordDetailResponse:
    """
    Build detailed service record response with status calculation
    """
    status, days_until = calculate_service_status(service_record.next_service_date)
    
    return schemas.ServiceRecordDetailResponse(
        id=service_record.id,
        vehicle_id=service_record.vehicle_id,
        vehicle_number=service_record.vehicle.vehicle_number,
        owner_name=service_record.vehicle.owner_name,
        model=service_record.vehicle.model,
        service_type_id=service_record.service_type_id,
        service_type_name=service_record.service_type.name,
        service_date=service_record.service_date,
        next_service_date=service_record.next_service_date,
        notes=service_record.notes,
        status=status,
        days_until_due=days_until
    )

def build_service_history(
    vehicle: models.Vehicle,
    service_records: List[models.ServiceRecord],
    db: Session
) -> schemas.ServiceHistoryResponse:
    """
    Build complete service history for a vehicle
    """
    detailed_records = [
        build_service_detail_response(record, db)
        for record in service_records
    ]
    
    return schemas.ServiceHistoryResponse(
        vehicle=schemas.VehicleResponse.from_orm(vehicle),
        service_records=detailed_records
    )

def generate_csv_data(service_records: List[models.ServiceRecord], db: Session) -> str:
    """
    Generate CSV data from service records
    Returns CSV string with headers
    """
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        "Service ID",
        "Vehicle Number",
        "Owner Name",
        "Model",
        "Service Type",
        "Service Date",
        "Next Service Date",
        "Status",
        "Days Until Due",
        "Notes"
    ])
    
    # Write data rows
    for record in service_records:
        status, days_until = calculate_service_status(record.next_service_date)
        writer.writerow([
            record.id,
            record.vehicle.vehicle_number,
            record.vehicle.owner_name,
            record.vehicle.model,
            record.service_type.name,
            record.service_date.strftime("%Y-%m-%d %H:%M:%S"),
            record.next_service_date.strftime("%Y-%m-%d %H:%M:%S"),
            status,
            days_until,
            record.notes or ""
        ])
    
    return output.getvalue()
