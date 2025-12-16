#!/usr/bin/env python3
import os
import sys
import time
import subprocess

def wait_for_db():
    """Wait for database to be ready"""
    print("Waiting for database...")
    
    while True:
        try:
            import psycopg
            conn = psycopg.connect(
                host=os.environ.get('DB_HOST', 'db'),
                port=os.environ.get('DB_PORT', '5432'),
                user=os.environ.get('DB_USER', 'postgres'),
                password=os.environ.get('DB_PASSWORD', 'Teqwa123'),
                dbname=os.environ.get('DB_NAME', 'postgres')
            )
            conn.close()
            print("Database is ready!")
            break
        except Exception as e:
            print(f"Database not ready: {e}")
            time.sleep(2)

def run_command(cmd):
    """Run a command and exit if it fails"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)

if __name__ == '__main__':
    print("=== Teqwa Backend Docker Entrypoint ===")
    
    # Wait for database
    wait_for_db()
    
    # Run migrations
    print("Running migrations...")
    run_command(['python', 'manage.py', 'migrate', '--noinput'])
    
    # Create superuser
    print("Creating superuser...")
    run_command(['python', 'manage.py', 'create_superuser_auto'])
    
    # Collect static files in production
    is_debug = os.environ.get('DEBUG', '1') == '1'
    if not is_debug:
        print("Collecting static files...")
        run_command(['python', 'manage.py', 'collectstatic', '--noinput'])
        
        # Start Production Server (Gunicorn)
        print("=== Starting Gunicorn Production Server ===")
        # We replace the current process with Gunicorn
        # Ensure gunicorn_config.py exists or pass arguments directly
        os.execvp('gunicorn', ['gunicorn', '-c', 'gunicorn_config.py', 'config.wsgi:application'])
    else:
        # Start Development Server
        print("=== Starting Django Development Server ===")
        os.execvp('python', ['python', 'manage.py', 'runserver', '0.0.0.0:8000'])