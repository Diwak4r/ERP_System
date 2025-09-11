from datetime import datetime, date
from models import SessionLocal, ProductionLog, Section
from sqlalchemy import func

def validate_material_flow(section_id, output_material, entry_date, db=None):
    """
    Validate material flow between sections
    Ensures that output from one section doesn't exceed available input
    """
    if not db:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False
    
    try:
        # Get the section
        section = db.query(Section).filter(Section.id == section_id).first()
        if not section:
            return {"valid": False, "error": "Section not found"}
        
        # If this section has a previous section (receives input from another section)
        previous_sections = db.query(Section).filter(Section.next_section_id == section_id).all()
        
        if previous_sections:
            # Calculate total available input from previous sections
            total_available_input = 0
            for prev_section in previous_sections:
                prev_output = db.query(func.sum(ProductionLog.output_material)).filter(
                    ProductionLog.section_id == prev_section.id,
                    ProductionLog.date == entry_date
                ).scalar() or 0
                total_available_input += prev_output
            
            # Calculate already consumed input by this section today
            already_consumed = db.query(func.sum(ProductionLog.input_material)).filter(
                ProductionLog.section_id == section_id,
                ProductionLog.date == entry_date
            ).scalar() or 0
            
            # Check if the new output would exceed available input
            if output_material > (total_available_input - already_consumed):
                return {
                    "valid": False,
                    "error": f"Insufficient input material. Available: {total_available_input - already_consumed}kg, Requested: {output_material}kg"
                }
        
        return {"valid": True}
        
    except Exception as e:
        return {"valid": False, "error": str(e)}
    finally:
        if close_db:
            db.close()

def validate_no_backdating(entry_date):
    """
    Validate that entries are not backdated
    """
    if isinstance(entry_date, str):
        entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
    
    if entry_date < date.today():
        return {"valid": False, "error": "Cannot backdate entries. Date must be today or future."}
    
    return {"valid": True}

def validate_production_data(data):
    """
    Comprehensive validation for production data
    """
    errors = []
    
    # Required fields
    required_fields = ['worker_id', 'item_id', 'date', 'actual', 'input_material', 'output_material']
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            errors.append(f"Field '{field}' is required")
    
    if errors:
        return {"valid": False, "errors": errors}
    
    try:
        # Validate data types and ranges
        actual = int(data['actual'])
        input_material = float(data['input_material'])
        output_material = float(data['output_material'])
        
        if actual < 0:
            errors.append("Actual production cannot be negative")
        
        if input_material < 0:
            errors.append("Input material cannot be negative")
        
        if output_material < 0:
            errors.append("Output material cannot be negative")
        
        if output_material > input_material:
            errors.append(f"Output material ({output_material}kg) cannot exceed input material ({input_material}kg)")
        
        # Validate date
        date_validation = validate_no_backdating(data['date'])
        if not date_validation['valid']:
            errors.append(date_validation['error'])
        
        if errors:
            return {"valid": False, "errors": errors}
        
        return {"valid": True}
        
    except ValueError as e:
        errors.append(f"Invalid data format: {str(e)}")
        return {"valid": False, "errors": errors}

def validate_attendance_data(data):
    """
    Validate attendance data
    """
    errors = []
    
    # Required fields
    if 'workers' not in data or not data['workers']:
        errors.append("At least one worker must be selected")
    
    if 'date' not in data:
        errors.append("Date is required")
    
    if errors:
        return {"valid": False, "errors": errors}
    
    # Validate date
    date_validation = validate_no_backdating(data['date'])
    if not date_validation['valid']:
        errors.append(date_validation['error'])
    
    # Validate worker IDs
    try:
        worker_ids = [int(w) for w in data['workers']]
        if any(w <= 0 for w in worker_ids):
            errors.append("Invalid worker ID")
    except ValueError:
        errors.append("Invalid worker ID format")
    
    if errors:
        return {"valid": False, "errors": errors}
    
    return {"valid": True}

def validate_downtime_data(data):
    """
    Validate machine downtime data
    """
    errors = []
    
    # Required fields
    required_fields = ['machine_name', 'start_time', 'end_time']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Field '{field}' is required")
    
    if errors:
        return {"valid": False, "errors": errors}
    
    try:
        # Validate datetime format and logic
        start_time = datetime.strptime(data['start_time'], '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(data['end_time'], '%Y-%m-%dT%H:%M')
        
        if start_time >= end_time:
            errors.append("End time must be after start time")
        
        if start_time.date() < date.today():
            errors.append("Cannot backdate downtime entries")
        
        # Check if downtime duration is reasonable (not more than 24 hours)
        duration_hours = (end_time - start_time).total_seconds() / 3600
        if duration_hours > 24:
            errors.append("Downtime duration cannot exceed 24 hours")
        
    except ValueError:
        errors.append("Invalid datetime format")
    
    if errors:
        return {"valid": False, "errors": errors}
    
    return {"valid": True}

def validate_requisition_data(data):
    """
    Validate requisition data
    """
    errors = []
    
    # Required fields
    required_fields = ['item_id', 'quantity']
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            errors.append(f"Field '{field}' is required")
    
    if errors:
        return {"valid": False, "errors": errors}
    
    try:
        quantity = int(data['quantity'])
        if quantity <= 0:
            errors.append("Quantity must be greater than 0")
    except ValueError:
        errors.append("Invalid quantity format")
    
    if errors:
        return {"valid": False, "errors": errors}
    
    return {"valid": True}

def check_data_integrity():
    """
    Check overall data integrity across the system
    Returns a report of any issues found
    """
    db = SessionLocal()
    issues = []
    
    try:
        # Check for material flow discrepancies
        sections = db.query(Section).all()
        
        for section in sections:
            if section.next_section_id:
                # Get today's data
                today = date.today()
                
                # Output from current section
                current_output = db.query(func.sum(ProductionLog.output_material)).filter(
                    ProductionLog.section_id == section.id,
                    ProductionLog.date == today
                ).scalar() or 0
                
                # Input to next section
                next_input = db.query(func.sum(ProductionLog.input_material)).filter(
                    ProductionLog.section_id == section.next_section_id,
                    ProductionLog.date == today
                ).scalar() or 0
                
                discrepancy = current_output - next_input
                if abs(discrepancy) > 0.1:  # Allow small rounding differences
                    next_section = db.query(Section).filter(Section.id == section.next_section_id).first()
                    issues.append({
                        "type": "material_flow",
                        "description": f"Material flow discrepancy between {section.name} and {next_section.name if next_section else 'Unknown'}",
                        "details": f"Output: {current_output}kg, Input: {next_input}kg, Discrepancy: {discrepancy}kg",
                        "severity": "high" if abs(discrepancy) > 10 else "medium"
                    })
        
        # Check for missing production data (workers with no entries today)
        from models import Worker
        today = date.today()
        workers_with_production = db.query(ProductionLog.worker_id).filter(
            ProductionLog.date == today
        ).distinct().all()
        worker_ids_with_production = [w[0] for w in workers_with_production]
        
        all_workers = db.query(Worker).all()
        for worker in all_workers:
            if worker.id not in worker_ids_with_production:
                issues.append({
                    "type": "missing_data",
                    "description": f"No production data for worker {worker.name} today",
                    "details": f"Worker ID: {worker.id}, Section: {worker.section.name if worker.section else 'Unknown'}",
                    "severity": "low"
                })
        
        return {"success": True, "issues": issues}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        db.close()

if __name__ == "__main__":
    # Test data integrity check
    result = check_data_integrity()
    print("Data Integrity Check Results:")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Issues found: {len(result['issues'])}")
        for issue in result['issues']:
            print(f"- {issue['type']}: {issue['description']} ({issue['severity']})")
    else:
        print(f"Error: {result['error']}")

