"""
Local testing script for Factory ERP system
This script sets up a local SQLite database for testing without Supabase
"""

import os
from sqlalchemy import create_engine
from models import Base, Worker, Item, Section, ProductionLog, Attendance, MachineDowntime, Requisition
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime

# Create local SQLite database
DATABASE_URL = "sqlite:///./local_test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_local_database():
    """Create tables and populate with sample data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Section).count() > 0:
            print("Database already has data. Skipping setup.")
            return
        
        # Create sections
        section1 = Section(name="Raw Material", next_section_id=None)
        section2 = Section(name="Processing", next_section_id=None)
        
        db.add(section1)
        db.add(section2)
        db.commit()
        
        # Update section1 to point to section2
        section1.next_section_id = section2.id
        db.commit()
        
        # Create workers
        workers = [
            Worker(name="Beer Bahadur", section_id=section1.id),
            Worker(name="Gita Devi", section_id=section1.id),
            Worker(name="Ram Prasad", section_id=section2.id),
            Worker(name="Sita Kumari", section_id=section2.id),
            Worker(name="Hari Krishna", section_id=section1.id)
        ]
        
        for worker in workers:
            db.add(worker)
        
        # Create items
        items = [
            Item(name="Khada Butta 6 inch", unit="pieces", default_target=100),
            Item(name="Corn Flour 1kg", unit="kg", default_target=50),
            Item(name="Soybean 500g", unit="kg", default_target=75),
            Item(name="Wheat Grain 2kg", unit="kg", default_target=120),
            Item(name="Rice 1kg", unit="kg", default_target=90),
            Item(name="Sugar 500g", unit="kg", default_target=60),
            Item(name="Salt 1kg", unit="kg", default_target=80),
            Item(name="Cooking Oil 1L", unit="liter", default_target=40),
            Item(name="Spices 200g", unit="pieces", default_target=30),
            Item(name="Packaging Material", unit="pieces", default_target=200)
        ]
        
        for item in items:
            db.add(item)
        
        db.commit()
        
        # Create sample production logs
        today = date.today()
        production_logs = [
            ProductionLog(
                worker_id=1, item_id=1, section_id=1, date=today,
                target=100, actual=75, input_material=400.0, output_material=350.0,
                wastage=50.0, overtime_hours=0.0
            ),
            ProductionLog(
                worker_id=2, item_id=2, section_id=1, date=today,
                target=50, actual=60, input_material=200.0, output_material=180.0,
                wastage=20.0, overtime_hours=2.0
            ),
            ProductionLog(
                worker_id=3, item_id=3, section_id=2, date=today,
                target=75, actual=70, input_material=150.0, output_material=140.0,
                wastage=10.0, overtime_hours=0.0
            ),
            ProductionLog(
                worker_id=4, item_id=4, section_id=2, date=today,
                target=120, actual=130, input_material=250.0, output_material=240.0,
                wastage=10.0, overtime_hours=0.67
            ),
            ProductionLog(
                worker_id=1, item_id=5, section_id=1, date=today,
                target=90, actual=85, input_material=300.0, output_material=280.0,
                wastage=20.0, overtime_hours=0.0
            )
        ]
        
        for log in production_logs:
            db.add(log)
        
        # Create sample attendance records
        attendance_records = [
            Attendance(worker_id=1, section_id=1, date=today, present=True),
            Attendance(worker_id=2, section_id=1, date=today, present=True),
            Attendance(worker_id=3, section_id=2, date=today, present=True),
            Attendance(worker_id=4, section_id=2, date=today, present=True),
            Attendance(worker_id=5, section_id=1, date=today, present=False)
        ]
        
        for record in attendance_records:
            db.add(record)
        
        # Create sample downtime records
        now = datetime.now()
        downtime_records = [
            MachineDowntime(
                section_id=1, machine_name="Machine1",
                start_time=now.replace(hour=9, minute=0),
                end_time=now.replace(hour=10, minute=0),
                remarks="Routine maintenance"
            ),
            MachineDowntime(
                section_id=2, machine_name="Machine2",
                start_time=now.replace(hour=14, minute=30),
                end_time=now.replace(hour=15, minute=0),
                remarks="Minor fault"
            )
        ]
        
        for record in downtime_records:
            db.add(record)
        
        # Create sample requisitions
        requisitions = [
            Requisition(item_id=1, section_id=1, quantity=10, status="pending"),
            Requisition(item_id=2, section_id=2, quantity=5, status="approved")
        ]
        
        for req in requisitions:
            db.add(req)
        
        db.commit()
        print("Local database setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        db.rollback()
    finally:
        db.close()

def run_local_app():
    """Run the Flask app with local SQLite database"""
    # Set environment variables for local testing
    os.environ['DATABASE_URL'] = DATABASE_URL
    os.environ['SECRET_KEY'] = 'local-testing-secret-key'
    os.environ['FLASK_ENV'] = 'development'
    
    # Import and modify models to use local database
    from models import SessionLocal as OriginalSessionLocal
    import models
    models.SessionLocal = SessionLocal
    
    # Import and run the app
    from app import app
    
    print("Starting local Flask app...")
    print("Access the app at: http://localhost:5000")
    print("Test accounts:")
    print("- Admin: admin@factory.com / pass123")
    print("- Staff: staff1@factory.com / pass123")
    
    app.run(host='0.0.0.0', debug=True, port=5000)

if __name__ == "__main__":
    setup_local_database()
    run_local_app()

