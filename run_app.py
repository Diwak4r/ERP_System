#!/usr/bin/env python3
"""
Production server runner for ERP system
"""
import os
from app import app

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Never use debug mode in production
    )