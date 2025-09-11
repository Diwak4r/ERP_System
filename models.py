from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, Date, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Worker(Base):
    __tablename__ = 'workers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    section_id = Column(Integer, ForeignKey('sections.id'))
    created_at = Column(DateTime, default=datetime.now)
    section = relationship('Section', back_populates='workers')

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    default_target = Column(Integer, nullable=False)

class Section(Base):
    __tablename__ = 'sections'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    next_section_id = Column(Integer, ForeignKey('sections.id'), nullable=True)
    workers = relationship('Worker', back_populates='section')
    production_logs = relationship('ProductionLog', back_populates='section')
    attendance_records = relationship('Attendance', back_populates='section')
    machine_downtimes = relationship('MachineDowntime', back_populates='section')
    requisitions = relationship('Requisition', back_populates='section')

class ProductionLog(Base):
    __tablename__ = 'production_logs'
    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey('workers.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    section_id = Column(Integer, ForeignKey('sections.id'))
    date = Column(Date, nullable=False)
    target = Column(Integer, nullable=False)
    actual = Column(Integer, nullable=False)
    input_material = Column(Float, nullable=False)
    output_material = Column(Float, nullable=False)
    wastage = Column(Float, nullable=False)
    overtime_hours = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    worker = relationship('Worker')
    item = relationship('Item')
    section = relationship('Section', back_populates='production_logs')

class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, ForeignKey('workers.id'))
    section_id = Column(Integer, ForeignKey('sections.id'))
    date = Column(Date, nullable=False)
    present = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    worker = relationship('Worker')
    section = relationship('Section', back_populates='attendance_records')

class MachineDowntime(Base):
    __tablename__ = 'machine_downtime'
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey('sections.id'))
    machine_name = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    remarks = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    section = relationship('Section', back_populates='machine_downtimes')

class Requisition(Base):
    __tablename__ = 'requisitions'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'))
    section_id = Column(Integer, ForeignKey('sections.id'))
    quantity = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default='pending') # pending, approved, rejected
    remarks = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    item = relationship('Item')
    section = relationship('Section', back_populates='requisitions')

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Determine database URL based on environment variables
if SUPABASE_URL and SUPABASE_KEY:
    DATABASE_URL = f"postgresql://postgres:{SUPABASE_KEY}@{SUPABASE_URL.split('//')[1]}/postgres"
else:
    # Fallback to SQLite for local development/testing if Supabase env vars are not set
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Initialize Supabase client only if environment variables are set
if SUPABASE_URL and SUPABASE_KEY:
    from supabase import create_client, Client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None # Placeholder for local testing without Supabase client

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# This part is for local testing with SQLite, not for Vercel deployment with Supabase
# if __name__ == '__main__':
#     Base.metadata.create_all(bind=engine)
#     print("Database tables created (for SQLite testing).")


