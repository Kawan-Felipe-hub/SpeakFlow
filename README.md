# SpeakFlow

SpeakFlow is a language learning platform powered by AI, featuring speech recognition, pronunciation assessment, and personalized tutoring for English conversational fluency.

## 🎯 Core Features

- **Voice Conversations**: Practice speaking with AI tutor using real-time speech recognition
- **Pronunciation Assessment**: Get objective feedback on your pronunciation with Azure Speech
- **Smart Flashcards**: AI-generated flashcards from conversation context using spaced repetition (SM-2)
- **Progress Tracking**: Monitor your learning journey with detailed metrics and streaks

## 🏗️ Project Structure

- **backend/** - Django 5 + Django Ninja + PostgreSQL API
  - Voice session management
  - Flashcard SRS system
  - User authentication and progress tracking
- **frontend/** - Next.js 14 web application
  - Voice conversation interface
  - Dashboard and flashcard management
- **mobile/** - Flutter companion app (separate project)
  - Offline-first flashcard review
  - SRS synchronization with backend

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Azure Speech Services API key
- Groq API key for LLM

### Setup (5 Commands)

```bash
# 1. Copy environment variables
cp .env.example .env

# 2. Edit .env and add your API keys
# Add GROQ_API_KEY, AZURE_SPEECH_KEY, AZURE_SPEECH_REGION

# 3. Start all services with Docker Compose
docker-compose up -d

# 4. Run Django migrations
docker-compose exec backend python manage.py migrate

# 5. Create a test user (optional)
docker-compose exec backend python criar_usuario_teste.py

# Access the applications
# Backend API: http://localhost:8000/api/
# Frontend: http://localhost:3000
```

## 🔧 Development Commands

```bash
# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild specific service
docker-compose up -d --build backend

# Access Django shell
docker-compose exec backend python manage.py shell

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Run tests
docker-compose exec backend python manage.py test
```

## 🔑 Environment Variables

Required environment variables in `.env`:

### Backend
- `DJANGO_SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection string
- `GROQ_API_KEY` - Groq API key for LLM
- `AZURE_SPEECH_KEY` - Azure Speech Services key
- `AZURE_SPEECH_REGION` - Azure region (e.g., brazilsouth)
- `AZURE_SPEECH_LANGUAGE` - Speech language (en-US)
- `AZURE_SPEECH_VOICE` - TTS voice (en-US-JennyNeural)

### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL

### Authentication
- `JWT_SIGNING_KEY` - JWT token signing key
- `JWT_ACCESS_TTL_MINUTES` - Access token lifetime (default: 15)
- `JWT_REFRESH_TTL_DAYS` - Refresh token lifetime (default: 30)

## 📱 Mobile App

The Flutter mobile app is maintained as a separate project:
- **Location**: `/dev/SpeakFlow_Mobile/`
- **Purpose**: Offline-first flashcard review companion
- **Features**: SRS algorithm, sync with backend, local SQLite storage
- **Status**: Independent development with API integration

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js Web   │    │  Django Backend │    │  External APIs  │
│                 │    │                 │    │                 │
│ • Voice UI      │◄──►│ • Session Mgmt  │◄──►│ • Azure Speech  │
│ • Dashboard     │    │ • SRS System   │    │ • Groq LLM     │
│ • Flashcards    │    │ • Auth (JWT)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  PostgreSQL DB  │    │  Flutter Mobile │
│                 │    │                 │
│ • Users         │    │ • Offline SRS   │
│ • Sessions      │    │ • Local SQLite  │
│ • Flashcards    │    │ • Sync Worker   │
└─────────────────┘    └─────────────────┘
```

## 🚀 Railway Deployment

### Backend Deployment
```bash
cd backend
railway up
```

### Frontend Deployment  
```bash
cd frontend  
railway up
```

### Required Railway Secrets
Set these in your Railway dashboard:
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `JWT_SIGNING_KEY`
- `GROQ_API_KEY`
- `AZURE_SPEECH_KEY`
- `AZURE_SPEECH_REGION`
- `AZURE_SPEECH_LANGUAGE`
- `AZURE_SPEECH_VOICE`
- `NEXT_PUBLIC_API_URL` (frontend only)

## 🧪 Testing

```bash
# Backend tests
docker-compose exec backend python manage.py test

# Frontend tests
cd frontend && npm test

# API testing
curl http://localhost:8000/api/docs
```

## 📊 Current Status

- ✅ **Web MVP**: Voice conversations, flashcards, SRS
- ✅ **Backend API**: Complete REST API with authentication
- 🔄 **Mobile App**: Separate project, basic SRS implemented
- 🚧 **Advanced Features**: Progress tracking, analytics in development

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.
