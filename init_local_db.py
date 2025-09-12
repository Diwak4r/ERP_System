#!/usr/bin/env python3
"""
Initialize local SQLite database with sample data for testing
"""
import os
os.environ['USE_LOCAL_DB'] = 'true'
os.environ['DATABASE_URL'] = 'sqlite:///./local_test.db'

from sqlalchemy import create_engine
from models import Base, Worker, Item, Section, ProductionLog, Attendance, MachineDowntime, Requisition
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime, timedelta

# Create local SQLite database
DATABASE_URL = "sqlite:///./local_test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database with tables and sample data"""
    print("Creating database tables...")
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=engine)
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Adding sections...")
        # Create sections
        section1 = Section(id=1, name="Raw Material", next_section_id=2)
        section2 = Section(id=2, name="Processing", next_section_id=3)
        section3 = Section(id=3, name="Finishing", next_section_id=4)
        section4 = Section(id=4, name="Packaging", next_section_id=None)
        
        db.add_all([section1, section2, section3, section4])
        db.commit()
        
        print("Adding workers...")
        # Create workers
        workers = [
            Worker(name="Beer Bahadur", section_id=1),
            Worker(name="Gita Devi", section_id=1),
            Worker(name="Ram Prasad", section_id=2),
            Worker(name="Sita Kumari", section_id=2),
            Worker(name="Hari Krishna", section_id=3),
            Worker(name="Lakshmi Sharma", section_id=3),
            Worker(name="Krishna Thapa", section_id=4),
            Worker(name="Maya Rai", section_id=4),
        ]
        
        db.add_all(workers)
        db.commit()
        
        print("Adding items...")
        # Create items
        items = [
            Item(name="Raw Cotton", unit="kg", default_target=500),
            Item(name="Processed Yarn", unit="kg", default_target=450),
            Item(name="Finished Fabric", unit="meters", default_target=1000),
            Item(name="Packaged Rolls", unit="units", default_target=50),
            Item(name="Thread Spools", unit="units", default_target=200),
        ]
        
        db.add_all(items)
        db.commit()
        
        print("Adding sample production logs...")
        # Add some sample production logs for today and yesterday
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        production_logs = [
            # Yesterday's data
            ProductionLog(
                worker_id=1, item_id=1, section_id=1,
                date=yesterday, target=500, actual=480,
                input_material=500, output_material=480,
                wastage=20, overtime_hours=1.5
            ),
            ProductionLog(
                worker_id=3, item_id=2, section_id=2,
                date=yesterday, target=450, actual=440,
                input_material=480, output_material=440,
                wastage=40, overtime_hours=2.0
            ),
            # Today's data
            ProductionLog(
                worker_id=2, item_id=1, section_id=1,
                date=today, target=500, actual=490,
                input_material=500, output_material=490,
                wastage=10, overtime_hours=0.5
            ),
        ]
        
        db.add_all(production_logs)
        db.commit()
        
        print("Adding sample attendance records...")
        # Add attendance records
        attendance_records = [
            Attendance(worker_id=1, section_id=1, date=yesterday, present=True),
            Attendance(worker_id=2, section_id=1, date=yesterday, present=True),
            Attendance(worker_id=3, section_id=2, date=yesterday, present=True),
            Attendance(worker_id=4, section_id=2, date=yesterday, present=False),
            Attendance(worker_id=1, section_id=1, date=today, present=True),
            Attendance(worker_id=2, section_id=1, date=today, present=True),
        ]
        
        db.add_all(attendance_records)
        db.commit()
        
        print("Adding sample machine downtime records...")
        # Add machine downtime records
        downtime_records = [
            MachineDowntime(
                section_id=1,
                machine_name="Cotton Processor #1",
                start_time=datetime.now() - timedelta(hours=3),
                end_time=datetime.now() - timedelta(hours=2),
                remarks="Belt replacement"
            ),
            MachineDowntime(
                section_id=2,
                machine_name="Spinning Machine #3",
                start_time=datetime.now() - timedelta(hours=1),
                end_time=datetime.now() - timedelta(minutes=30),
                remarks="Routine maintenance"
            ),
        ]
        
        db.add_all(downtime_records)
        db.commit()
        
        print("Adding sample requisitions...")
        # Add requisitions
        requisitions = [
            Requisition(
                item_id=1, section_id=1,
                quantity=100, status="approved",
                remarks="Monthly stock replenishment"
            ),
            Requisition(
                item_id=2, section_id=2,
                quantity=50, status="pending",
                remarks="Additional material needed for rush order"
            ),
            Requisition(
                item_id=5, section_id=3,
                quantity=200, status="pending",
                remarks="Running low on thread spools"
            ),
        ]
        
        db.add_all(requisitions)
        db.commit()
        
        print("\n✅ Database initialized successfully!")
        print("\nDatabase Statistics:")
        print(f"  - Sections: {db.query(Section).count()}")
        print(f"  - Workers: {db.query(Worker).count()}")
        print(f"  - Items: {db.query(Item).count()}")
        print(f"  - Production Logs: {db.query(ProductionLog).count()}")
        print(f"  - Attendance Records: {db.query(Attendance).count()}")
        print(f"  - Machine Downtimes: {db.query(MachineDowntime).count()}")
        print(f"  - Requisitions: {db.query(Requisition).count()}")
        
        print("\n📝 Test Credentials:")
        print("  Admin: admin@factory.com / pass123")
        print("  Staff 1: staff1@factory.com / pass123 (Raw Material Section)")
        print("  Staff 2: staff2@factory.com / pass123 (Processing Section)")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()