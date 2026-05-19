# OPTIVA — Lead Intelligence System

<div align="center">

![Optiva](https://img.shields.io/badge/OPTIVA-Lead%20Intelligence%20System-E94560?style=for-the-badge&labelColor=1A1A2E)

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=flat-square&logo=django&logoColor=white)](https://djangoproject.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-77.13%25-FF6600?style=flat-square)](https://xgboost.readthedocs.io)
[![Celery](https://img.shields.io/badge/Celery-RabbitMQ-37814A?style=flat-square)](https://docs.celeryq.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)

**Intelligent Commercial Lead Qualification System**



</div>

---

## Project Repositories

This project is split into two repositories:

| Repository | Description | Link |
|---|---|---|
| **optiva-backend** | Django + ML Pipeline + Celery + PostgreSQL | Current repo |
| **optiva-frontend** | React 18 + TypeScript — Dashboards | [github.com/cuervo0102/Optiva-frontend](https://github.com/cuervo0102/Optiva-frontend) |

> The backend exposes a REST API on `http://localhost:8000`
> The frontend connects automatically via Axios + JWT

---

## Table of Contents

- [Overview](#overview)
- [Frontend](#frontend)
- [AI Pipeline](#ai-pipeline)
- [ML Results](#ml-results)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Backend Installation](#backend-installation)
- [Running the Project](#running-the-project)
- [API Endpoints](#api-endpoints)
- [Roles & Permissions](#roles--permissions)
- [Project Structure](#project-structure)
- [Team](#team)

---

## Overview

Optiva automatically analyzes recorded sales call audio to qualify prospects in real time.

```
Audio (M4A / WAV / MP3)
        ↓
  FFmpeg — Convert to WAV 16kHz mono
        ↓
  Faster-Whisper — Audio → Text transcription
        ↓
  TF-IDF → SVD → StandardScaler → XGBoost
  Interest score 0 → 100%
        ↓
Score >= 65%?
  YES → Qualified lead → Sales assistant + Excel export
  NO  → Not interested → Data Analyst dashboard
```

### Business Impact

| Metric | Before | After |
|---|---|---|
| Conversion rate | 15% | 35% (+133%) |
| Lead qualification time | Hours (manual) | 35 seconds |
| Cold leads contacted | 60% | 20% (-67%) |

---

## Frontend

[![Frontend](https://img.shields.io/badge/Frontend-React%2018%20+%20TypeScript-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://github.com/cuervo0102/Optiva-frontend)

> **Frontend Repository:** https://github.com/cuervo0102/Optiva-frontend

### Frontend Technologies

- React 18 + TypeScript
- Axios with automatic JWT interceptors
- React Router — role-based protected navigation
- 5 dashboards: Login, Commercial, Assistant, Analyst, Manager

### Running the Frontend

```bash
git clone https://github.com/cuervo0102/Optiva-frontend.git
cd Optiva-frontend
npm install
npm start
```

> Available at `http://localhost:3000`
> Backend must be running at `http://localhost:8000`

---

## AI Pipeline

### Transcription — Faster-Whisper

```python
# Audio conversion before transcription
subprocess.run([
    "ffmpeg", "-i", "call.m4a",
    "-ar", "16000", "-ac", "1", "-y", "call.wav"
])

# Transcription
model = WhisperModel("base", device="cpu", compute_type="int8")
segments, _ = model.transcribe("call.wav", language="en")
text = " ".join(seg.text for seg in segments)
```

### Vectorization — TF-IDF + SVD

```
Raw text
    → TF-IDF  (max_features=5000, ngram_range=(1,2))
    → TruncatedSVD  (n_components=200)
    → StandardScaler
    → 200-dimensional vector
```

### Classification — XGBoost

```python
X = tfidf.transform([text])
X = svd.transform(X)
X = scaler.transform(X)
proba = float(xgb.predict_proba(X)[0][1])
# proba >= 0.65 → INTERESTED
```

### Contact Extraction — Regex

```python
# Standard email AND Whisper format ("X at gmail.com")
# Phone number (Moroccan + international formats)
# Client name extraction
```

---

## ML Results

| Metric | Value |
|---|---|
| **Accuracy** | **77.13%** |
| **F1-Score** | **0.773** |
| Data Leakage | **Zero** |
| Early Stopping | Iteration 1147 |
| Training Dataset | 100,000 conversations |
| Qualification Threshold | Score >= 65% |

### Data Leakage Detected and Removed

| Removed Feature | Correlation \|r\| |
|---|---|
| customer_engagement | 0.784 |
| sales_effectiveness | 0.856 |
| probability_trajectory | computed from outcome |

> With leakage: 98.95% (artificial) → Without leakage: **77.13%** (real)

### Approach Comparison

| Approach | Accuracy | Decision |
|---|---|---|
| **TF-IDF + SVD + XGBoost** | **77.13%** | Selected |
| Sentence Embeddings MiniLM | 59.49% | Dropped |
| Sentence Embeddings MPNet | 59.70% | Dropped |

---

## Architecture

| Layer | Technology | Role |
|---|---|---|
| ASR | Faster-Whisper | Audio transcription |
| ML | TF-IDF + SVD + XGBoost | Interest scoring |
| Conversion | FFmpeg | M4A/MP3 → WAV |
| API | Django 4.2 + DRF | Secured REST API |
| Auth | JWT (SimpleJWT) | Authentication |
| Async | Celery + RabbitMQ | Background ML processing |
| Database | PostgreSQL 15 | Data persistence |
| Cache | Redis | Cache + Celery results |
| Export | openpyxl | Excel file generation |

---

## Prerequisites

- Python 3.11+
- PostgreSQL 15
- Redis (WSL Ubuntu recommended on Windows)
- RabbitMQ (WSL Ubuntu recommended on Windows)
- FFmpeg
- scikit-learn **1.6.1** (exact version required for .pkl compatibility)

---

## Backend Installation

### 1. Clone the repository

```bash
git clone https://github.com/cuervo0102/optiva-backend.git
cd optiva-backend
```

### 2. Virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django==4.2.9 djangorestframework djangorestframework-simplejwt
pip install django-cors-headers psycopg2-binary redis celery
pip install django-celery-results python-dotenv openpyxl drf-spectacular
pip install django-filter pillow faster-whisper scikit-learn==1.6.1 xgboost
```

### 4. Environment variables

Create `.env` at the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=optiva
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=7

ML_MODELS_DIR=ml/models
WHISPER_MODEL_SIZE=base
WHISPER_DEVICE=cpu
```

### 5. Database setup

```bash
psql -U postgres -c "CREATE DATABASE optiva;"
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. ML Models

Download the `.pkl` files from Kaggle Output and place them in `ml/models/`:

```
ml/models/
├── tfidf_model.pkl
├── svd_model.pkl
├── scaler_tfidf.pkl
└── model_tfidf_v2.pkl
```

---

## Running the Project

### Step 1 — Start services (WSL Ubuntu)

```bash
sudo service redis-server start
sudo service rabbitmq-server start

# Verify
redis-cli ping                  # → PONG
sudo rabbitmq-diagnostics ping  # → Ping succeeded
```

### Step 2 — Terminal 1 — Django

```bash
python manage.py runserver
```

### Step 3 — Terminal 2 — Celery Worker

```bash
# Windows (pool=solo required)
celery -A config worker --loglevel=info --pool=solo

# Linux / Mac
celery -A config worker --loglevel=info
```

### Step 4 — Terminal 3 — Frontend

```bash
git clone https://github.com/cuervo0102/Optiva-frontend.git
cd Optiva-frontend
npm install && npm start
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/api/auth/login/` | Login + JWT tokens | Public |
| POST | `/api/auth/logout/` | Logout + blacklist | Auth |
| POST | `/api/auth/refresh/` | Refresh access token | Auth |
| GET/PUT | `/api/auth/me/` | User profile | Auth |
| POST | `/api/auth/change-password/` | Change password | Auth |
| GET | `/api/auth/users/` | List users | Admin |
| POST | `/api/auth/users/create/` | Create user | Admin |
| POST | `/api/auth/users/<id>/unlock/` | Unlock account | Admin |

### Conversations & Leads

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/api/conversations/upload/` | Upload audio file | Commercial |
| GET | `/api/conversations/` | List conversations | Commercial |
| GET | `/api/leads/interested/` | Interested leads | Assistant |
| GET | `/api/leads/export/` | Download Excel file | Assistant |
| GET | `/api/leads/all/` | All leads | Analyst |
| GET | `/api/leads/analytics/summary/` | Global statistics | Manager |

### Interactive API Documentation

```
http://localhost:8000/api/docs/    ← Swagger UI
```

---

## Roles & Permissions

| Role | Access |
|---|---|
| **Commercial** | Upload audio, view own conversations and scores |
| **Assistant** | Interested leads, update status, export Excel |
| **Data Analyst** | All leads, rejection analysis |
| **Manager** | Global dashboard, per-commercial stats |
| **Admin** | Full user management |

### Security Features

- JWT Access Token (60 min) + Refresh Token (7 days)
- Token blacklist after logout
- Account lockout after 5 failed login attempts
- Manual unlock by admin
- CNSS field write_only — never exposed in API responses
- CORS restricted to localhost:3000
- Soft delete — deactivation without physical deletion

---

## Project Structure

```
optiva-backend/
├── .env                         ← Environment variables (git ignored)
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── ml/
│   ├── pipeline.py              ← Whisper + TF-IDF + SVD + XGBoost
│   └── models/                  ← .pkl model files
├── users/                       ← Auth + JWT + Roles
├── conversations/               ← Audio upload + Celery tasks
├── leads/                       ← Leads + Excel export + Analytics
└── media/
    ├── audio/                   ← Uploaded audio files
    ├── exports/                 ← Generated Excel files
    └── profiles/                ← User profile pictures
```

> Frontend repository: https://github.com/cuervo0102/Optiva-frontend




