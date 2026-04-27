# SpeakFlow

SpeakFlow is a language learning platform powered by AI, featuring speech recognition, pronunciation assessment, and personalized tutoring.

## Project Structure

- **backend** - Django 5 + Django Ninja + PostgreSQL API
- **frontend** - Next.js 14 web application
- **landing** - Next.js 14 landing page

## Local Development Setup

### Prerequisites
- Docker and Docker Compose installed

### Quick Start (5 Commands)

```bash
# 1. Copy environment variables
cp .env.example .env

# 2. Edit .env and add your API keys (GROQ_API_KEY, AZURE_SPEECH_KEY)
# Open .env in your editor and replace the placeholder values

# 3. Start all services with Docker Compose
docker-compose up -d

# 4. Run Django migrations (inside the backend container)
docker-compose exec backend python manage.py migrate

# 5. Access the applications
# Backend API: http://localhost:8000/api/
# Frontend: http://localhost:3000
# Landing: http://localhost:3001
```

### Additional Commands

```bash
# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop services and remove volumes
docker-compose down -v

# Rebuild a specific service
docker-compose up -d --build backend

# Access Django shell
docker-compose exec backend python manage.py shell
```

## Environment Variables

See `.env.example` for all required environment variables:

- **DJANGO_SECRET_KEY** - Django secret key (generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- **DATABASE_URL** - PostgreSQL connection string
- **GROQ_API_KEY** - Groq API key for LLM
- **AZURE_SPEECH_KEY** - Azure Speech Services key
- **AZURE_SPEECH_REGION** - Azure region (e.g., brazilsouth)
- **NEXT_PUBLIC_API_URL** - Backend API URL for frontend

## Railway Deployment

Each service has its own `railway.toml` configuration file:

1. **Backend**: Deploy the `/backend` directory to Railway
2. **Frontend**: Deploy the `/frontend` directory to Railway
3. **Landing**: Deploy the `/landing` directory to Railway

### Railway Setup Steps

1. Create a new Railway project
2. Add a PostgreSQL service
3. Deploy each service from its respective directory
4. Set environment variables in Railway dashboard (replace `{VARIABLE}` placeholders in railway.toml)
5. Set `NEXT_PUBLIC_API_URL` in frontend/landing to point to the backend Railway URL

### Required Railway Secrets

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS` (comma-separated list of domains)
- `JWT_SIGNING_KEY`
- `GROQ_API_KEY`
- `AZURE_SPEECH_KEY`
- `AZURE_SPEECH_REGION`
- `AZURE_SPEECH_LANGUAGE`
- `AZURE_SPEECH_VOICE`
- `NEXT_PUBLIC_API_URL` (for frontend and landing)

## Development Without Docker

If you prefer to run services locally without Docker:

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Landing

```bash
cd landing
npm install
npm run dev
```

## API Documentation

Once the backend is running, visit:
- API Docs: http://localhost:8000/api/docs
- Interactive API: http://localhost:8000/api/

## License

MIT
