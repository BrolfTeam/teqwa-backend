import os
import multiprocessing

# Use PORT environment variable (set by platform) or fallback to 8000
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"

# Limit workers to 2 for low-memory plans
workers = 2

# Optional: number of threads per worker
threads = 2

# Request timeout in seconds
timeout = 120

# Keep-alive for connections
keepalive = 5

# Logs: output to stdout/stderr (standard for containerized deployments)
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Allow proxy headers (e.g., X-Forwarded-For)
forwarded_allow_ips = "*"
