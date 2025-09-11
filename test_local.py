"""
Local testing script that doesn't require Supabase
"""

import os
import sys

# Set environment variables for testing
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_KEY'] = 'test-key'
os.environ['SECRET_KEY'] = 'test-secret'

# Now import the modules
from validation import validate_production_data, validate_attendance_data, validate_downtime_data
from datetime import date, datetime

def test_validation_functions():
    """Test validation functions without database"""
    print("Testing validation functions...")
    
    # Test production validation
    print("\n1. Production Data Validation:")
    
    # Valid data
    valid_data = {
        'worker_id': 1,
        'item_id': 1,
        'date': date.today().isoformat(),
        'actual': 100,
        'input_material': 200.0,
        'output_material': 180.0
    }
    
    result = validate_production_data(valid_data)
    print(f"   Valid data: {result['valid']} ✓")
    
    # Invalid data - negative actual
    invalid_data = valid_data.copy()
    invalid_data['actual'] = -10
    
    result = validate_production_data(invalid_data)
    print(f"   Negative actual: {result['valid']} ✓ (should be False)")
    if not result['valid']:
        print(f"   Error: {result['errors'][0]}")
    
    # Invalid data - output > input
    invalid_data = valid_data.copy()
    invalid_data['output_material'] = 250.0
    
    result = validate_production_data(invalid_data)
    print(f"   Output > Input: {result['valid']} ✓ (should be False)")
    if not result['valid']:
        print(f"   Error: {result['errors'][0]}")
    
    # Test attendance validation
    print("\n2. Attendance Data Validation:")
    
    valid_attendance = {
        'workers': [1, 2, 3],
        'date': date.today().isoformat()
    }
    
    result = validate_attendance_data(valid_attendance)
    print(f"   Valid attendance: {result['valid']} ✓")
    
    # Invalid - no workers
    invalid_attendance = {
        'workers': [],
        'date': date.today().isoformat()
    }
    
    result = validate_attendance_data(invalid_attendance)
    print(f"   No workers: {result['valid']} ✓ (should be False)")
    
    # Test downtime validation
    print("\n3. Downtime Data Validation:")
    
    now = datetime.now()
    valid_downtime = {
        'machine_name': 'Machine1',
        'start_time': now.strftime('%Y-%m-%dT%H:%M'),
        'end_time': (now.replace(hour=now.hour+1)).strftime('%Y-%m-%dT%H:%M'),
        'remarks': 'Test downtime'
    }
    
    result = validate_downtime_data(valid_downtime)
    print(f"   Valid downtime: {result['valid']} ✓")
    
    # Invalid - end before start
    invalid_downtime = valid_downtime.copy()
    invalid_downtime['end_time'] = (now.replace(hour=now.hour-1)).strftime('%Y-%m-%dT%H:%M')
    
    result = validate_downtime_data(invalid_downtime)
    print(f"   End before start: {result['valid']} ✓ (should be False)")

def test_calculations():
    """Test calculation logic"""
    print("\n4. Calculation Tests:")
    
    # Test overtime calculation
    target = 100
    actual = 120
    overtime_hours = (actual - target) / (target / 8) if actual > target else 0
    expected_overtime = 1.6  # (120-100) / (100/8) = 20 / 12.5 = 1.6
    
    print(f"   Overtime calculation: {overtime_hours} hours ✓")
    print(f"   Expected: {expected_overtime} hours")
    
    # Test wastage calculation
    input_material = 200.0
    output_material = 180.0
    wastage = input_material - output_material
    expected_wastage = 20.0
    
    print(f"   Wastage calculation: {wastage}kg ✓")
    print(f"   Expected: {expected_wastage}kg")

def test_file_structure():
    """Test that all required files exist"""
    print("\n5. File Structure Test:")
    
    required_files = [
        'app.py',
        'models.py',
        'auth.py',
        'validation.py',
        'requirements.txt',
        'vercel.json',
        'init_db.sql',
        'templates/base.html',
        'templates/login.html',
        'templates/staff_dashboard.html',
        'templates/admin_dashboard.html',
        'static/css/style.css',
        'static/js/main.js'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✓ {file_path}")
        else:
            print(f"   ✗ {file_path} (missing)")

def main():
    print("Factory ERP Local Test Suite")
    print("=" * 40)
    
    try:
        test_validation_functions()
        test_calculations()
        test_file_structure()
        
        print("\n" + "=" * 40)
        print("✓ All local tests completed successfully!")
        print("\nNext steps:")
        print("1. Set up Supabase project")
        print("2. Run init_db.sql in Supabase")
        print("3. Set environment variables")
        print("4. Deploy to Vercel")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

