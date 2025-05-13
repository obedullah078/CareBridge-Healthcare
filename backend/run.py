import os
import sys

# Manually read the .env file
if os.path.exists('.env'):
    env_vars = {}
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value

from app import create_app, db
from app.models import User, Appointment, Availability
from config import Config

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Appointment': Appointment,
        'Availability': Availability
    }

if __name__ == '__main__':
    # Get the port from environment variable, defaulting to 5001 if not set
    port = int(os.environ.get('PORT', 5001))
    
    # Print debug information to help with connection issues
    print(f"Starting server on 0.0.0.0:{port}")
    print(f"The server will be accessible via:")
    print(f"  - http://127.0.0.1:{port}")
    print(f"  - http://localhost:{port}")
    
    # Add CORS headers to ensure frontend can connect
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # Run with host set to '0.0.0.0' to bind to all interfaces
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
