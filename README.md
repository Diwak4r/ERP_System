# Factory ERP System

A comprehensive Factory Production Tracking ERP system built with Python Flask, Supabase (PostgreSQL), and deployable to Vercel serverless platform.

## Features

### 🔐 Authentication & Authorization
- Role-based access control (Staff & Admin)
- Supabase Authentication with JWT tokens
- Secure password handling
- Session management

### 📊 Production Tracking
- Daily production entry with auto-calculations
- Target vs Actual tracking
- Material flow validation
- Overtime hours calculation
- Wastage tracking

### 👥 Staff Management
- Worker attendance tracking
- Section-based access control
- Individual worker performance history

### 🔧 Machine Management
- Machine downtime recording
- Duration tracking with alerts
- Maintenance remarks

### 📋 Store Requisitions
- Item requisition system
- Admin approval workflow
- Status tracking (Pending/Approved/Rejected)

### 📈 Admin Dashboard
- Production performance charts
- Real-time summary cards
- Material flow monitoring
- Data integrity checks

### 🛡️ Data Integrity
- No backdating prevention
- Material flow validation
- Input/output balance checks
- Comprehensive error handling

## Tech Stack

- **Backend**: Python Flask with SQLAlchemy
- **Database**: Supabase (PostgreSQL)
- **Frontend**: Bootstrap 5 + Chart.js
- **Authentication**: Supabase Auth
- **Deployment**: Vercel Serverless
- **Validation**: Custom validation layer

## Quick Start

### 1. Local Development

```bash
# Clone the repository
git clone <repository-url>
cd factory_erp

# Install dependencies
pip install -r requirements.txt

# Run local tests
python test_local.py

# For local testing with SQLite (no Supabase required)
python local_test.py
```

### 2. Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to Settings > API to get your project URL and anon key
3. In the SQL Editor, run the contents of `init_db.sql`
4. Enable Row Level Security (RLS) if needed

### 3. Environment Variables

Create a `.env` file (use `.env.example` as template):

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SECRET_KEY=your_secret_key_here
```

### 4. Vercel Deployment

1. Push code to GitHub repository
2. Connect repository to Vercel
3. Set environment variables in Vercel dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_KEY` 
   - `SECRET_KEY`
4. Deploy!

## Project Structure

```
factory_erp/
├── app.py                 # Main Flask application
├── models.py              # Database models (SQLAlchemy)
├── auth.py                # Authentication logic
├── validation.py          # Data validation functions
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel deployment config
├── runtime.txt           # Python version for deployment
├── init_db.sql           # Database initialization script
├── .env.example          # Environment variables template
├── local_test.py         # Local testing with SQLite
├── test_local.py         # Validation tests
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── staff_dashboard.html
│   └── admin_dashboard.html
└── static/               # Static assets
    ├── css/style.css
    └── js/main.js
```

## API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /logout` - Logout

### Staff Dashboard
- `GET /staff` - Staff dashboard
- `POST /api/production` - Submit production data
- `POST /api/attendance` - Submit attendance
- `POST /api/downtime` - Record machine downtime
- `POST /api/requisition` - Submit requisition

### Admin Dashboard
- `GET /admin` - Admin dashboard
- `GET /api/reports/production` - Production reports
- `GET /api/reports/attendance` - Attendance reports
- `GET /api/reports/downtime` - Downtime reports
- `GET /api/reports/material_flow` - Material flow analysis
- `GET /api/worker_history/<id>` - Worker performance history
- `POST /api/requisition/<id>/<action>` - Approve/reject requisitions
- `GET /api/data_integrity` - Data integrity check

## Database Schema

### Core Tables
- **sections**: Production sections with flow relationships
- **workers**: Worker information and section assignments
- **items**: Product items with targets and units
- **production_logs**: Daily production entries
- **attendance**: Worker attendance records
- **machine_downtime**: Machine downtime tracking
- **requisitions**: Store requisition requests

### Key Relationships
- Workers belong to sections
- Production logs link workers, items, and sections
- Sections can have next_section_id for material flow
- Material flow validation ensures output ≤ input

## Validation Rules

### Production Data
- No backdating (date ≥ today)
- Positive values only
- Output material ≤ Input material
- Material flow validation between sections

### Attendance
- At least one worker must be selected
- No backdating allowed

### Machine Downtime
- End time > Start time
- Duration ≤ 24 hours
- No backdating allowed

## Test Accounts

For testing purposes, create these accounts in Supabase Auth:

- **Admin**: admin@factory.com / pass123
- **Staff 1**: staff1@factory.com / pass123 (Section: Raw Material)
- **Staff 2**: staff2@factory.com / pass123 (Section: Processing)

## Features Highlights

### Excel-like UI
- Responsive Bootstrap design
- Mobile-friendly forms
- Table-based data display
- Auto-calculations

### Material Flow Tracking
- Section-to-section material validation
- Real-time discrepancy detection
- Flow balance monitoring

### Security Features
- JWT token authentication
- Role-based access control
- Input validation and sanitization
- CORS enabled for API access

### Performance Optimizations
- Efficient database queries
- Lightweight serverless deployment
- Optimized for Vercel free tier

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check SUPABASE_URL and SUPABASE_KEY
   - Ensure Supabase project is active
   - Verify database tables exist

2. **Authentication Issues**
   - Check if users exist in Supabase Auth
   - Verify user metadata (role, section_id)
   - Check JWT token configuration

3. **Deployment Issues**
   - Ensure all environment variables are set in Vercel
   - Check Python version compatibility
   - Verify requirements.txt is complete

### Local Testing

Run `python test_local.py` to verify:
- ✅ Validation functions
- ✅ Calculation logic
- ✅ File structure
- ✅ Basic functionality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test locally
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test output
3. Check Vercel deployment logs
4. Verify Supabase configuration

---

**Built with ❤️ for efficient factory production management**

