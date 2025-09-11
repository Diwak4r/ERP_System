from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_cors import CORS
from models import SessionLocal, Worker, Item, Section, ProductionLog, Attendance, MachineDowntime, Requisition
from auth import login_user, register_user, require_auth, require_role, get_user_role
from validation import validate_production_data, validate_attendance_data, validate_downtime_data, validate_requisition_data, validate_material_flow, check_data_integrity
from datetime import datetime, date
from dotenv import load_dotenv
from sqlalchemy import func
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
CORS(app)  # Enable CORS for all routes

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

@app.route("/")
def index():
    if 'user' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('staff_dashboard'))
    return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        result = login_user(email, password)
        if result['success']:
            session['user'] = result['user']
            session['role'] = result['role']
            session['token'] = result['session'].access_token if result['session'] else None
            
            flash('Login successful!', 'success')
            if result['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('staff_dashboard'))
        else:
            flash(result['error'], 'error')
    
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route("/staff")
def staff_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    
    # Get user's section
    user_section_id = session['user'].user_metadata.get('section_id', 1)
    
    # Get workers in user's section
    workers = db.query(Worker).filter(Worker.section_id == user_section_id).all()
    
    # Get all items
    items = db.query(Item).all()
    
    # Get user's section
    section = db.query(Section).filter(Section.id == user_section_id).first()
    
    return render_template('staff_dashboard.html', 
                         workers=workers, 
                         items=items, 
                         section=section)

@app.route("/admin")
def admin_dashboard():
    if 'user' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    db = get_db()
    
    # Get summary data
    total_workers = db.query(Worker).count()
    total_sections = db.query(Section).count()
    pending_requisitions = db.query(Requisition).filter(Requisition.status == 'pending').count()
    
    # Get today's production summary
    today = date.today()
    today_production = db.query(ProductionLog).filter(ProductionLog.date == today).all()
    
    production_summary = {
        'total_target': sum(p.target for p in today_production),
        'total_actual': sum(p.actual for p in today_production),
        'total_wastage': sum(p.wastage for p in today_production)
    }
    
    # Get pending requisitions
    pending_reqs = db.query(Requisition).filter(Requisition.status == 'pending').all()
    
    return render_template('admin_dashboard.html',
                         total_workers=total_workers,
                         total_sections=total_sections,
                         pending_requisitions=pending_requisitions,
                         production_summary=production_summary,
                         pending_reqs=pending_reqs)

# API Routes

@app.route("/api/production", methods=['POST'])
def api_production():
    if 'user' not in session:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    
    try:
        data = request.get_json()
        
        # Validate input data
        validation_result = validate_production_data(data)
        if not validation_result['valid']:
            return jsonify({"success": False, "errors": validation_result['errors']}), 400
        
        db = get_db()
        
        # Get item to auto-fill target
        item = db.query(Item).filter(Item.id == data['item_id']).first()
        if not item:
            return jsonify({"success": False, "error": "Item not found"}), 404
        
        # Calculate fields
        target = item.default_target
        actual = int(data['actual'])
        input_material = float(data['input_material'])
        output_material = float(data['output_material'])
        wastage = input_material - output_material
        entry_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        # Calculate overtime hours
        overtime_hours = 0
        if actual > target:
            overtime_hours = (actual - target) / (target / 8)
        
        # Material flow validation
        user_section_id = session['user'].user_metadata.get('section_id', 1)
        
        material_flow_validation = validate_material_flow(user_section_id, output_material, entry_date, db)
        if not material_flow_validation['valid']:
            return jsonify({"success": False, "error": material_flow_validation['error']}), 400
        
        # Create production log
        production_log = ProductionLog(
            worker_id=data['worker_id'],
            item_id=data['item_id'],
            section_id=user_section_id,
            date=entry_date,
            target=target,
            actual=actual,
            input_material=input_material,
            output_material=output_material,
            wastage=wastage,
            overtime_hours=overtime_hours
        )
        
        db.add(production_log)
        db.commit()
        
        return jsonify({"success": True, "message": "Production data saved successfully"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/attendance", methods=['POST'])
def api_attendance():
    if 'user' not in session:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    
    try:
        data = request.get_json()
        
        # Validate input data
        validation_result = validate_attendance_data(data)
        if not validation_result['valid']:
            return jsonify({"success": False, "errors": validation_result['errors']}), 400
        
        db = get_db()
        entry_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        user_section_id = session['user'].user_metadata.get('section_id', 1)
        
        # Create attendance records for selected workers
        for worker_id in data['workers']:
            attendance = Attendance(
                worker_id=int(worker_id),
                section_id=user_section_id,
                date=entry_date,
                present=True
            )
            db.add(attendance)
        
        db.commit()
        
        return jsonify({"success": True, "message": "Attendance saved successfully"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/downtime", methods=['POST'])
def api_downtime():
    if 'user' not in session:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    
    try:
        data = request.get_json()
        
        # Validate input data
        validation_result = validate_downtime_data(data)
        if not validation_result['valid']:
            return jsonify({"success": False, "errors": validation_result['errors']}), 400
        
        db = get_db()
        
        # Parse validated times
        start_time = datetime.strptime(data['start_time'], '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(data['end_time'], '%Y-%m-%dT%H:%M')
        
        user_section_id = session['user'].user_metadata.get('section_id', 1)
        
        downtime = MachineDowntime(
            section_id=user_section_id,
            machine_name=data['machine_name'],
            start_time=start_time,
            end_time=end_time,
            remarks=data.get('remarks', '')
        )
        
        db.add(downtime)
        db.commit()
        
        return jsonify({"success": True, "message": "Downtime recorded successfully"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/requisition", methods=['POST'])
def api_requisition():
    if 'user' not in session:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    
    try:
        data = request.get_json()
        
        # Validate input data
        validation_result = validate_requisition_data(data)
        if not validation_result['valid']:
            return jsonify({"success": False, "errors": validation_result['errors']}), 400
        
        db = get_db()
        user_section_id = session['user'].user_metadata.get('section_id', 1)
        
        requisition = Requisition(
            item_id=data['item_id'],
            section_id=user_section_id,
            quantity=int(data['quantity']),
            status='pending'
        )
        
        db.add(requisition)
        db.commit()
        
        return jsonify({"success": True, "message": "Requisition submitted successfully"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Admin API Routes

@app.route("/api/reports/production", methods=['GET'])
def api_reports_production():
    if 'user' not in session or session.get('role') != 'admin':
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    try:
        db = get_db()
        
        # Get production data grouped by item
        production_data = db.query(
            Item.name,
            func.sum(ProductionLog.target).label('total_target'),
            func.sum(ProductionLog.actual).label('total_actual')
        ).join(ProductionLog).group_by(Item.name).all()
        
        labels = [p.name for p in production_data]
        targets = [int(p.total_target) for p in production_data]
        actuals = [int(p.total_actual) for p in production_data]
        
        return jsonify({
            "success": True,
            "labels": labels,
            "targets": targets,
            "actuals": actuals
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/reports/attendance", methods=['GET'])
def api_reports_attendance():
    if 'user' not in session or session.get('role') != 'admin':
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    try:
        db = get_db()
        
        # Get attendance data by section
        attendance_data = db.query(
            Section.name,
            func.count(Attendance.id).label('present_count')
        ).join(Attendance).filter(Attendance.present == True).group_by(Section.name).all()
        
        return jsonify({
            "success": True,
            "data": [{"section": a.name, "present": a.present_count} for a in attendance_data]
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/reports/downtime", methods=['GET'])
def api_reports_downtime():
    if 'user' not in session or session.get('role') != 'admin':
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    try:
        db = get_db()
        
        # Get recent downtime records
        downtime_records = db.query(MachineDowntime).order_by(MachineDowntime.created_at.desc()).limit(20).all()
        
        data = []
        for record in downtime_records:
            duration_hours = (record.end_time - record.start_time).total_seconds() / 3600
            data.append({
                "machine": record.machine_name,
                "start_time": record.start_time.isoformat(),
                "end_time": record.end_time.isoformat(),
                "duration_hours": round(duration_hours, 2),
                "remarks": record.remarks,
                "is_long": duration_hours > 1
            })
        
        return jsonify({
            "success": True,
            "data": data
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/worker_history/<int:worker_id>", methods=['GET'])
def api_worker_history(worker_id):
    if 'user' not in session or session.get('role') != 'admin':
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    try:
        db = get_db()
        
        # Get worker's production history
        history = db.query(ProductionLog, Item.name).join(Item).filter(
            ProductionLog.worker_id == worker_id
        ).order_by(ProductionLog.date.desc()).limit(30).all()
        
        data = []
        for log, item_name in history:
            data.append({
                "date": log.date.isoformat(),
                "item_name": item_name,
                "target": log.target,
                "actual": log.actual,
                "efficiency": round((log.actual / log.target) * 100, 1) if log.target > 0 else 0
            })
        
        return jsonify({
            "success": True,
            "history": data
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/requisition/<int:requisition_id>/<action>", methods=['POST'])
def api_requisition_action(requisition_id, action):
    if 'user' not in session or session.get('role') != 'admin':
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    if action not in ['approve', 'reject']:
        return jsonify({"success": False, "error": "Invalid action"}), 400
    
    try:
        db = get_db()
        data = request.get_json() or {}
        
        requisition = db.query(Requisition).filter(Requisition.id == requisition_id).first()
        if not requisition:
            return jsonify({"success": False, "error": "Requisition not found"}), 404
        
        requisition.status = 'approved' if action == 'approve' else 'rejected'
        requisition.remarks = data.get('remarks', '')
        
        db.commit()
        
        return jsonify({"success": True, "message": f"Requisition {action}d successfully"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/reports/material_flow", methods=['GET'])
def api_reports_material_flow():
    if 'user' not in session or session.get('role') != 'admin':
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    try:
        db = get_db()
        
        # Get material flow data
        sections = db.query(Section).all()
        flow_data = []
        
        for section in sections:
            if section.next_section_id:
                # Get output from current section
                current_output = db.query(func.sum(ProductionLog.output_material)).filter(
                    ProductionLog.section_id == section.id,
                    ProductionLog.date == date.today()
                ).scalar() or 0
                
                # Get input for next section
                next_input = db.query(func.sum(ProductionLog.input_material)).filter(
                    ProductionLog.section_id == section.next_section_id,
                    ProductionLog.date == date.today()
                ).scalar() or 0
                
                discrepancy = current_output - next_input
                
                flow_data.append({
                    "from_section": section.name,
                    "to_section": db.query(Section).filter(Section.id == section.next_section_id).first().name,
                    "output": current_output,
                    "input": next_input,
                    "discrepancy": discrepancy,
                    "has_issue": abs(discrepancy) > 0.1  # Flag if discrepancy > 0.1kg
                })
        
        return jsonify({
            "success": True,
            "data": flow_data
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/test_db")
def test_db():
    try:
        db = get_db()
        sections = db.query(Section).all()
        section_names = [s.name for s in sections]
        return jsonify({"status": "success", "sections": section_names})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)


@app.route("/api/data_integrity", methods=['GET'])
def api_data_integrity():
    if 'user' not in session or session.get('role') != 'admin':
        return jsonify({"success": False, "error": "Admin access required"}), 403
    
    try:
        result = check_data_integrity()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

