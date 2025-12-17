# 🕌 Teqwa Backend API

Django REST Framework backend for the Teqwa mosque management platform.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- pip

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd teqwa-backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env  # Copy example file
   # Or for development:
   cp .env.development.example .env
   # Edit .env with your settings
   ```

5. **Set up database**:
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000`

## 🐳 Docker Development

### Using Docker Compose

```bash
docker compose up --build
```

This will start:
- PostgreSQL database (port 5433)
- Django backend (port 8000)

### Environment Variables

Create a `.env` file in the root directory:

```env
# Django Settings
DEBUG=1
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

# Frontend URL (for CORS and email links)
FRONTEND_URL=http://localhost:5173

# CORS (comma-separated list)
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@teqwa.com

# Payment Gateway (Chapa)
CHAPA_SECRET_KEY=your-chapa-secret-key

# AWS S3 (for production media files)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=us-east-1
```

## 📚 API Documentation

Once the server is running, access:
- **Swagger UI**: http://localhost:8000/api/docs/
- **API Root**: http://localhost:8000/api/v1/
- **Admin Panel**: http://localhost:8000/admin/

## 🏗️ Project Structure

```
teqwa-backend/
├── config/              # Django project settings
│   ├── settings.py      # Main settings
│   ├── urls.py          # URL routing
│   └── wsgi.py          # WSGI config
├── authentication/      # User authentication
├── accounts/            # User accounts and profiles
├── events/              # Event management
├── donations/           # Donation system
├── education/           # Educational services
├── futsal_booking/      # Futsal court booking
├── payments/            # Payment processing
├── staff/               # Staff management
├── announcements/       # News and announcements
├── itikaf/              # Iʿtikāf program
├── contact/             # Contact form
├── memberships/         # Membership management
├── students/            # Student management
├── TeqwaCore/           # Core utilities
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
└── Dockerfile           # Docker configuration
```

## 🔧 Development Commands

```bash
# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic

# Django shell
python manage.py shell
```

## 🚀 Production Deployment

See `PRODUCTION_GUIDE.md` for detailed deployment instructions.

### Key Points

- Set `DEBUG=False` in production
- Configure `ALLOWED_HOSTS` with your domain
- Set `FRONTEND_URL` to your frontend domain
- Configure `CORS_ALLOWED_ORIGINS` properly
- Use a production database (PostgreSQL)
- Set up email service (Gmail, SendGrid, AWS SES, etc.)
- Configure AWS S3 for media files (optional)
- Use Gunicorn with Nginx reverse proxy

### Running with Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --config gunicorn_config.py
```

## 🔐 Security

- JWT authentication
- CORS protection
- CSRF protection
- Rate limiting
- HTTPS enforcement in production
- Secure cookie settings

## 📝 API Endpoints

- `/api/v1/auth/` - Authentication (login, register, password reset)
- `/api/v1/accounts/` - User accounts and profiles
- `/api/v1/events/` - Event management
- `/api/v1/donations/` - Donation causes and transactions
- `/api/v1/payments/` - Payment processing
- `/api/v1/education/` - Educational services
- `/api/v1/futsal/` - Futsal court booking
- `/api/v1/staff/` - Staff management
- `/api/v1/announcements/` - News and announcements
- `/api/v1/itikaf/` - Iʿtikāf program
- `/api/v1/students/` - Student management

See `/api/docs/` for complete API documentation.

## 🔗 Related Repositories

- **Frontend**: [teqwa-frontend](https://github.com/your-org/teqwa-frontend)

## 📄 License

MIT License

## 🤝 Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.
