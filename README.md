# 🎬 Online Cinema Platform

[![codecov](https://codecov.io/gh/iSevenpwnz/Online-Cinema-Project/branch/main/graph/badge.svg)](https://codecov.io/gh/iSevenpwnz/Online-Cinema-Project)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**A modern, production-ready online cinema platform with comprehensive API, automated deployment, and microservices architecture built with Python/FastAPI.**

## 📋 Table of Contents

- [🎯 Project Overview](#-project-overview)
- [✨ Key Features](#-key-features)
- [🏗️ Architecture](#️-architecture)
- [📁 Project Structure](#-project-structure)
- [🚀 Quick Start](#-quick-start)
- [🔧 Configuration](#-configuration)
- [📚 API Documentation](#-api-documentation)
- [💻 Usage Guide](#-usage-guide)
- [🧪 Testing](#-testing)
- [🚢 Deployment](#-deployment)
- [📊 Monitoring](#-monitoring)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🎯 Project Overview

Online Cinema Platform is a comprehensive cinema management system built with modern Python technologies and microservices architecture. The platform provides complete functionality for managing movies, users, payments, and content delivery in a scalable, production-ready environment.

This project demonstrates enterprise-level software development practices including:

- **Clean Architecture** with separation of concerns
- **Async/Await** patterns for high performance
- **Microservices** design with Docker containerization
- **CI/CD Pipeline** with GitHub Actions
- **Comprehensive Testing** strategy (Unit/Integration/E2E)
- **Production Deployment** with automated monitoring

### 🎥 Who is this project for?

- **Backend Developers** - Learning modern Python/FastAPI architecture patterns
- **Startups** - Ready-to-use foundation for online cinema platforms
- **Students** - Enterprise-level application example with best practices
- **DevOps Engineers** - Reference CI/CD pipeline implementation
- **Technical Leads** - Microservices architecture blueprint

## ✨ Key Features

### 🔐 Authentication & Authorization

- **JWT-based Authentication** with access/refresh token rotation
- **Role-based Access Control** (User, Admin, Moderator)
- **Secure Registration/Login** with bcrypt password hashing
- **Email Verification** system with MailHog integration
- **OAuth2 Bearer** token scheme with automatic expiration

### 🎬 Content Management System

- **Full Movie Management** with CRUD operations (30KB+ codebase)
- **Category & Genre Classification** with hierarchical structure
- **Rating & Review System** with aggregated scores
- **Advanced Search & Filtering** with multiple criteria
- **File Upload System** via MinIO S3-compatible storage
- **Content Metadata** management with rich descriptions

### 🛒 E-commerce Functionality

- **Shopping Cart System** with session persistence (6.8KB implementation)
- **Order Management** with status tracking (4.7KB codebase)
- **Stripe Payment Integration** with webhooks (5.9KB implementation)
- **Purchase History** and invoice generation
- **Digital Content Delivery** after successful payment

### 👤 User Profile Management

- **Personal User Profiles** with customizable settings (5.2KB)
- **Watchlist & Favorites** with collection management
- **Viewing History** with progress tracking
- **User Preferences** and notification settings
- **Account Management** comprehensive system (31KB codebase)

### 🔧 Advanced Technical Features

- **Asynchronous Task Processing** via Celery + Redis
- **Real-time Notifications** with email templates
- **Smart Pagination** for large datasets with FastAPI-pagination
- **Rate Limiting & Security** with request throttling
- **Comprehensive Logging** with structured data
- **Health Monitoring** with automated alerts

## 🏗️ Architecture

### 🔧 Technology Stack

#### 🔥 Backend Core

- **FastAPI 0.115+** - Modern async web framework with automatic API docs
- **Python 3.10+** - Typed Python with async/await support
- **SQLAlchemy 2.0** - Async ORM with declarative models
- **Alembic** - Database schema migrations management
- **Pydantic 2.0** - Data validation and serialization

#### 🗄️ Databases & Storage

- **PostgreSQL 15+** - Primary relational database
- **Redis 6.2+** - Caching and Celery message broker
- **MinIO** - S3-compatible object storage for files
- **SQLite** - Alternative database for testing

#### 🔒 Security & Authentication

- **JWT (python-jose)** - Stateless authentication tokens
- **bcrypt** - Secure password hashing
- **OAuth2 Bearer** - Token-based authorization
- **CORS middleware** - Cross-origin request security

#### ⚡ Async & Background Processing

- **Celery 5.5+** - Distributed task queue system
- **Redis** - Message broker and result backend
- **HTTPX** - Async HTTP client for external APIs
- **asyncio** - Native Python asynchronous programming

#### 🧪 Testing & Quality Assurance

- **pytest 8.3+** - Test framework with async support
- **pytest-cov** - Code coverage reporting
- **mypy** - Static type checking
- **flake8** - Code style linting
- **codecov** - Coverage tracking and reporting

#### 🐳 DevOps & Infrastructure

- **Docker & Docker Compose** - Containerization and orchestration
- **GitHub Actions** - CI/CD pipeline automation
- **Nginx** - Reverse proxy and static file serving
- **Gunicorn + Uvicorn** - ASGI production server

#### 💳 External Integrations

- **Stripe API** - Payment processing and webhooks
- **MailHog** - Email testing in development environment
- **boto3/aioboto3** - AWS S3 compatibility (MinIO integration)

## 📁 Project Structure

```
Online-Cinema-Project/
├── 🚀 src/                              # Main application source code
│   ├── 📱 main.py                       # FastAPI application entry point (126 lines)
│   ├── ⚙️  config/                      # Application configuration
│   │   ├── settings.py                  # Environment-based settings
│   │   └── dependencies.py              # Dependency injection setup
│   ├── 🗄️  database/                    # Database layer
│   │   ├── __init__.py                  # Database initialization (996B)
│   │   ├── models/                      # SQLAlchemy ORM models
│   │   │   ├── base.py                  # Base model class (149B)
│   │   │   ├── accounts.py              # User & authentication models (7.9KB)
│   │   │   ├── movies.py                # Movie catalog models (5.5KB)
│   │   │   ├── orders.py                # Order management models (1.8KB)
│   │   │   ├── payments.py              # Payment transaction models (2.2KB)
│   │   │   ├── shopping_cart.py         # Shopping cart models (1.5KB)
│   │   │   ├── comments.py              # Review & comment models (1.9KB)
│   │   │   └── extra_functionality_movie.py # Extended movie features (2.0KB)
│   │   ├── migrations/                  # Alembic database migrations
│   │   │   └── versions/                # Migration version files
│   │   ├── validators/                  # Database-level validators
│   │   ├── pagination/                  # Custom pagination logic
│   │   ├── seed_data/                   # Initial data for development
│   │   ├── source/                      # Data source utilities
│   │   ├── session_postgresql.py        # PostgreSQL session config (1.9KB)
│   │   ├── session_sqlite.py            # SQLite session config (2.0KB)
│   │   ├── db_sync.py                   # Sync database utilities (460B)
│   │   └── populate.py                  # Database seeding script (17KB)
│   ├── 🌐 routes/                       # API endpoint definitions
│   │   ├── __init__.py                  # Router exports (475B)
│   │   ├── accounts.py                  # Authentication endpoints (31KB, 926 lines)
│   │   ├── movies.py                    # Movie management API (30KB, 1007 lines)
│   │   ├── extra_functionality_movie.py # Extended movie features (14KB, 454 lines)
│   │   ├── shopping_cart.py             # Shopping cart API (6.8KB, 224 lines)
│   │   ├── payments.py                  # Stripe payment endpoints (5.9KB, 188 lines)
│   │   ├── profiles.py                  # User profile management (5.2KB, 149 lines)
│   │   ├── orders.py                    # Order processing API (4.7KB, 123 lines)
│   │   └── comments.py                  # Comment & review API (2.8KB, 96 lines)
│   ├── 📋 schemas/                      # Pydantic data validation schemas
│   │   ├── __init__.py                  # Schema exports (808B)
│   │   ├── movies.py                    # Movie data schemas (6.2KB, 251 lines)
│   │   ├── payments.py                  # Payment validation schemas (2.5KB, 99 lines)
│   │   ├── accounts.py                  # User account schemas (1.8KB, 86 lines)
│   │   ├── profiles.py                  # Profile management schemas (1.6KB, 66 lines)
│   │   ├── shopping_cart.py             # Cart validation schemas (1.3KB, 51 lines)
│   │   ├── orders.py                    # Order processing schemas (1.0KB, 43 lines)
│   │   ├── comments.py                  # Comment schemas (795B, 44 lines)
│   │   ├── extra_functionality_movie.py # Extended feature schemas (669B, 32 lines)
│   │   └── examples/                    # Schema example data
│   ├── 🔒 security/                     # Authentication & authorization
│   │   ├── auth.py                      # JWT token management
│   │   ├── permissions.py               # Role-based access control
│   │   └── utils.py                     # Security utility functions
│   ├── 💾 storages/                     # External storage integrations
│   │   ├── minio_client.py              # MinIO S3-compatible storage
│   │   └── file_manager.py              # File upload/download logic
│   ├── 📧 notifications/                # Notification system
│   │   ├── email_service.py             # Email sending logic
│   │   └── templates/                   # Email HTML templates
│   ├── ⚡ celery_config/                # Background task processing
│   │   ├── celery_worker.py             # Celery worker configuration
│   │   └── tasks.py                     # Async task definitions
│   ├── 🔍 validation/                   # Business logic validation
│   │   └── business_rules.py            # Custom validation rules
│   ├── 🚨 exceptions/                   # Custom exception handling
│   │   ├── base.py                      # Base exception classes
│   │   └── handlers.py                  # FastAPI exception handlers
│   ├── 🧪 tests/                        # Application test suite
│   │   ├── conftest.py                  # Pytest configuration (11KB, 350 lines)
│   │   ├── unit/                        # Unit tests for individual components
│   │   ├── test_integration/            # Integration tests for services
│   │   ├── test_e2e/                    # End-to-end API tests
│   │   └── doubles/                     # Test doubles (mocks, stubs, fakes)
│   │       ├── fakes/                   # Fake implementations for testing
│   │       └── stubs/                   # Method stubs for isolation
│   └── 🛠️  services/                    # Business logic layer
│       ├── __init__.py                  # Service exports (59B)
│       ├── shopping_cart.py             # Cart business logic (5.8KB, 163 lines)
│       ├── orders.py                    # Order processing logic (4.3KB, 120 lines)
│       └── payments/                    # Payment service modules
├── 🐳 docker/                           # Docker configuration files
│   ├── nginx/                           # Nginx reverse proxy setup
│   │   ├── Dockerfile                   # Nginx container build
│   │   └── .env                         # Nginx environment variables
│   ├── mailhog/                         # Email testing service
│   │   └── Dockerfile                   # MailHog container setup
│   ├── minio_mc/                        # MinIO client configuration
│   │   └── Dockerfile                   # MinIO management client
│   └── tests/                           # Test environment containers
│       └── Dockerfile                   # Test runner container
├── ⚙️  configs/                         # External service configurations
│   └── nginx/                           # Nginx configuration files
│       └── nginx.conf                   # Production Nginx config
├── 🛠️  commands/                        # Automation and deployment scripts
│   ├── deploy.sh                        # Production deployment script
│   ├── check-status.sh                  # Health check and monitoring
│   ├── setup-server.sh                  # Initial server configuration
│   ├── run_web_server_prod.sh           # Production server startup
│   ├── run_migration.sh                 # Database migration runner
│   └── setup_minio.sh                   # MinIO bucket initialization
├── 🔄 .github/                          # GitHub Actions CI/CD
│   └── workflows/                       # Automated workflows
│       └── cd.yml                       # Continuous deployment pipeline
├── 📊 tests/                            # Additional test suites
│   ├── conftest.py                      # Global test configuration
│   └── unit/                            # Top-level unit tests
├── 📄 Configuration Files               # Project configuration
│   ├── docker-compose-dev.yml           # Development environment (4.0KB)
│   ├── docker-compose-prod.yml          # Production environment (4.8KB)
│   ├── docker-compose-tests.yml         # Testing environment (2.4KB)
│   ├── Dockerfile                       # Main application container (1.2KB)
│   ├── alembic.ini                      # Database migration config (3.9KB)
│   ├── pyproject.toml                   # Python dependencies & config (1.6KB)
│   ├── poetry.lock                      # Locked dependency versions (311KB)
│   ├── pytest.ini                       # Test runner configuration
│   ├── .env.example                     # Environment variables template
│   ├── .flake8                          # Code style configuration
│   ├── .codecov.yml                     # Coverage reporting config
│   ├── .gitignore                       # Git ignore patterns
│   └── init.sql                         # Database initialization script
└── 📚 Documentation                     # Project documentation
    ├── README.md                        # This comprehensive guide
    └── DEPLOYMENT.md                    # Deployment documentation (if exists)
```

### 📊 Code Metrics Summary

| Component    | Files     | Lines of Code | Size   | Purpose                         |
| ------------ | --------- | ------------- | ------ | ------------------------------- |
| **Routes**   | 9 files   | ~3,500 lines  | ~120KB | API endpoint definitions        |
| **Models**   | 8 files   | ~650 lines    | ~23KB  | Database schema definitions     |
| **Schemas**  | 9 files   | ~770 lines    | ~16KB  | Data validation & serialization |
| **Services** | 3 files   | ~400 lines    | ~10KB  | Business logic implementation   |
| **Tests**    | Multiple  | ~2,000+ lines | ~50KB+ | Comprehensive test coverage     |
| **Config**   | 10+ files | ~500 lines    | ~20KB  | Infrastructure & deployment     |

## 🚀 Quick Start

### 📋 Prerequisites

- **Python 3.10+** installed on your system
- **Docker & Docker Compose** for containerization
- **Poetry** for Python dependency management
- **Git** for version control
- **8GB+ RAM** recommended for full stack

### 🔧 Local Development Setup

1. **Clone the Repository**

```bash
git clone https://github.com/iSevenpwnz/Online-Cinema-Project.git
cd Online-Cinema-Project
```

2. **Environment Configuration**

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env  # or use your preferred editor
```

3. **Install Dependencies**

```bash
# Using Poetry (recommended)
poetry install
poetry shell

# Or using pip
pip install -r requirements.txt
```

4. **Start Development Environment**

```bash
# Launch all services with Docker Compose
docker-compose -f docker-compose-dev.yml up -d

# Check service status
docker-compose -f docker-compose-dev.yml ps
```

5. **Initialize Database**

```bash
# Run database migrations
docker-compose -f docker-compose-dev.yml exec web alembic upgrade head

# Seed initial data (optional)
docker-compose -f docker-compose-dev.yml exec web python -m database.populate
```

6. **Access the Services**

| Service               | URL                               | Purpose                   |
| --------------------- | --------------------------------- | ------------------------- |
| **API Documentation** | http://localhost:8000/api/v1/docs | Interactive Swagger UI    |
| **Main Application**  | http://localhost:8000             | FastAPI backend           |
| **PgAdmin**           | http://localhost:3333             | Database management       |
| **MailHog**           | http://localhost:8025             | Email testing interface   |
| **MinIO Console**     | http://localhost:9001             | Object storage management |
| **RedisInsight**      | http://localhost:5540             | Redis database viewer     |

## 🔧 Configuration

### 🌍 Environment Variables

Create a `.env` file based on `.env.example` with the following configuration:

```bash
# Database Configuration
POSTGRES_DB=movies_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_HOST=postgres_theater
POSTGRES_DB_PORT=5432

# JWT Security Configuration
SECRET_KEY_ACCESS=your_access_secret_key_minimum_32_characters
SECRET_KEY_REFRESH=your_refresh_secret_key_minimum_32_characters
JWT_SIGNING_ALGORITHM=HS256

# Email Configuration (MailHog for development)
EMAIL_HOST=mailhog_theater
EMAIL_PORT=1025
EMAIL_HOST_USER=testuser
EMAIL_HOST_PASSWORD=test_password
EMAIL_USE_TLS=False

# Object Storage Configuration (MinIO)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_minio_password_here
MINIO_HOST=minio-theater
MINIO_PORT=9000
MINIO_STORAGE=theater-storage

# Payment Integration (Stripe)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key

# Redis Configuration
REDIS_HOST=redis_theater
REDIS_PORT=6379
REDIS_DB=0

# Application Settings
LOG_LEVEL=debug
ENVIRONMENT=development
API_V1_PREFIX=/api/v1
```

### 🔒 Security Configuration

#### JWT Token Settings

```python
# Token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Algorithm and key requirements
JWT_ALGORITHM = "HS256"
SECRET_KEY_LENGTH_MINIMUM = 32  # characters
```

#### CORS Configuration

```python
# Allowed origins for CORS
BACKEND_CORS_ORIGINS = [
    "http://localhost:3000",  # React frontend
    "http://localhost:8080",  # Vue frontend
    "https://yourdomain.com"  # Production domain
]
```

## 📚 API Documentation

### 🔗 Interactive Documentation

The API provides comprehensive interactive documentation:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json

### 🎯 Core API Endpoints

#### 🔐 Authentication System (`/api/v1/accounts/`)

| Method | Endpoint            | Description               | Auth Required |
| ------ | ------------------- | ------------------------- | ------------- |
| `POST` | `/register/`        | Create new user account   | ❌            |
| `POST` | `/login/`           | Login and get JWT tokens  | ❌            |
| `POST` | `/refresh/`         | Refresh access token      | ❌            |
| `POST` | `/logout/`          | Logout current user       | ✅            |
| `GET`  | `/profile/`         | Get current user profile  | ✅            |
| `PUT`  | `/profile/`         | Update user profile       | ✅            |
| `POST` | `/verify-email/`    | Verify email address      | ❌            |
| `POST` | `/forgot-password/` | Request password reset    | ❌            |
| `POST` | `/reset-password/`  | Reset password with token | ❌            |

#### 🎬 Movie Management (`/api/v1/theater/`)

| Method   | Endpoint                      | Description              | Auth Required | Admin Only |
| -------- | ----------------------------- | ------------------------ | ------------- | ---------- |
| `GET`    | `/movies/`                    | List movies with filters | ❌            | ❌         |
| `POST`   | `/movies/`                    | Create new movie         | ✅            | ✅         |
| `GET`    | `/movies/{id}/`               | Get movie details        | ❌            | ❌         |
| `PUT`    | `/movies/{id}/`               | Update movie             | ✅            | ✅         |
| `DELETE` | `/movies/{id}/`               | Delete movie             | ✅            | ✅         |
| `GET`    | `/genres/`                    | List all genres          | ❌            | ❌         |
| `GET`    | `/categories/`                | List all categories      | ❌            | ❌         |
| `POST`   | `/movies/{id}/upload-poster/` | Upload movie poster      | ✅            | ✅         |

#### 🛒 Shopping Cart (`/shopping-cart/`)

| Method   | Endpoint                  | Description         | Auth Required |
| -------- | ------------------------- | ------------------- | ------------- |
| `GET`    | `/cart/`                  | Get current cart    | ✅            |
| `POST`   | `/cart/add/`              | Add movie to cart   | ✅            |
| `PUT`    | `/cart/update/{item_id}/` | Update cart item    | ✅            |
| `DELETE` | `/cart/remove/{item_id}/` | Remove from cart    | ✅            |
| `POST`   | `/cart/checkout/`         | Proceed to checkout | ✅            |
| `DELETE` | `/cart/clear/`            | Clear entire cart   | ✅            |

#### 💳 Payment Processing (`/api/v1/payments/`)

| Method | Endpoint                 | Description                  | Auth Required |
| ------ | ------------------------ | ---------------------------- | ------------- |
| `POST` | `/create-intent/`        | Create Stripe payment intent | ✅            |
| `POST` | `/confirm/`              | Confirm payment              | ✅            |
| `GET`  | `/history/`              | Get payment history          | ✅            |
| `POST` | `/webhook/`              | Stripe webhook handler       | ❌            |
| `GET`  | `/receipt/{payment_id}/` | Get payment receipt          | ✅            |

#### 📦 Order Management (`/api/v1/orders/`)

| Method | Endpoint               | Description         | Auth Required |
| ------ | ---------------------- | ------------------- | ------------- |
| `GET`  | `/`                    | List user orders    | ✅            |
| `POST` | `/`                    | Create new order    | ✅            |
| `GET`  | `/{order_id}/`         | Get order details   | ✅            |
| `PUT`  | `/{order_id}/status/`  | Update order status | ✅            |
| `GET`  | `/{order_id}/invoice/` | Download invoice    | ✅            |

#### 📝 Comments & Reviews (`/api/v1/comments/`)

| Method   | Endpoint              | Description         | Auth Required |
| -------- | --------------------- | ------------------- | ------------- |
| `GET`    | `/movie/{movie_id}/`  | Get movie comments  | ❌            |
| `POST`   | `/movie/{movie_id}/`  | Add comment/review  | ✅            |
| `PUT`    | `/{comment_id}/`      | Edit comment        | ✅            |
| `DELETE` | `/{comment_id}/`      | Delete comment      | ✅            |
| `POST`   | `/{comment_id}/like/` | Like/unlike comment | ✅            |

### 🔒 Authentication Usage

Most endpoints require JWT authentication. Here's how to use it:

1. **Register or Login**

```bash
# Register new user
curl -X POST "http://localhost:8000/api/v1/accounts/register/" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "secure_password123",
       "username": "moviefan"
     }'

# Login to get tokens
curl -X POST "http://localhost:8000/api/v1/accounts/login/" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "secure_password123"
     }'
```

2. **Use Access Token**

```bash
# Include token in Authorization header
curl -X GET "http://localhost:8000/api/v1/theater/movies/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

3. **Refresh Token When Expired**

```bash
curl -X POST "http://localhost:8000/api/v1/accounts/refresh/" \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

## 💻 Usage Guide

### 🎬 Complete Movie Management Workflow

1. **Admin: Add New Movie**

```bash
curl -X POST "http://localhost:8000/api/v1/theater/movies/" \
     -H "Authorization: Bearer ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "The Matrix",
       "description": "A computer hacker learns from mysterious rebels about the true nature of his reality.",
       "genre": "Sci-Fi",
       "duration": 136,
       "price": 12.99,
       "release_date": "1999-03-31"
     }'
```

2. **User: Browse Movies**

```bash
# Get movies with filters
curl "http://localhost:8000/api/v1/theater/movies/?genre=Sci-Fi&min_price=5&max_price=20&page=1&size=10"
```

3. **User: Add to Cart**

```bash
curl -X POST "http://localhost:8000/shopping-cart/cart/add/" \
     -H "Authorization: Bearer USER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "movie_id": 1,
       "quantity": 1
     }'
```

4. **User: Checkout Process**

```bash
# Create payment intent
curl -X POST "http://localhost:8000/api/v1/payments/create-intent/" \
     -H "Authorization: Bearer USER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "amount": 1299,
       "currency": "usd"
     }'

# Confirm payment (after Stripe processing)
curl -X POST "http://localhost:8000/api/v1/payments/confirm/" \
     -H "Authorization: Bearer USER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "payment_intent_id": "pi_1234567890"
     }'
```

### 🛠️ Development Workflow

1. **Running Tests During Development**

```bash
# Run specific test categories
pytest src/tests/unit/ -v                    # Unit tests only
pytest src/tests/test_integration/ -v        # Integration tests
pytest src/tests/test_e2e/ -v               # End-to-end tests

# Run with coverage
pytest --cov=src --cov-report=html

# Run tests in parallel
pytest -n auto
```

2. **Database Management**

```bash
# Create new migration
docker-compose -f docker-compose-dev.yml exec web alembic revision --autogenerate -m "Add new feature"

# Apply migrations
docker-compose -f docker-compose-dev.yml exec web alembic upgrade head

# Rollback migration
docker-compose -f docker-compose-dev.yml exec web alembic downgrade -1
```

3. **Monitoring Logs**

```bash
# View application logs
docker-compose -f docker-compose-dev.yml logs -f web

# View specific service logs
docker-compose -f docker-compose-dev.yml logs -f postgres_theater
docker-compose -f docker-compose-dev.yml logs -f redis_theater
docker-compose -f docker-compose-dev.yml logs -f celery_worker_theater
```

### 🔄 Background Tasks with Celery

The platform uses Celery for handling asynchronous tasks:

1. **Email Notifications**

```python
# Send welcome email (triggered automatically)
from celery_config.tasks import send_welcome_email
send_welcome_email.delay(user_id=123)
```

2. **Order Processing**

```python
# Process order after payment (automatic)
from celery_config.tasks import process_order
process_order.delay(order_id=456)
```

3. **Monitor Celery Workers**

```bash
# Check worker status
docker-compose -f docker-compose-dev.yml exec celery_worker celery -A celery_config.celery_worker.celery_app status

# Monitor tasks
docker-compose -f docker-compose-dev.yml exec celery_worker celery -A celery_config.celery_worker.celery_app events
```

## 🧪 Testing

### 🏃‍♂️ Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test types
pytest src/tests/unit/                    # Unit tests
pytest src/tests/test_integration/        # Integration tests
pytest src/tests/test_e2e/               # End-to-end tests

# Run tests in parallel (faster)
pytest -n auto

# Run specific test file
pytest src/tests/unit/test_accounts.py -v

# Run tests matching pattern
pytest -k "test_login" -v
```

### 📊 Test Coverage

The project maintains comprehensive test coverage:

- **Unit Tests**: Individual functions and methods
- **Integration Tests**: Service interactions and database operations
- **End-to-End Tests**: Complete API workflows
- **Mock Tests**: External service integrations

```bash
# Generate detailed HTML coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html  # View in browser
```

### 🐳 Testing in Docker Environment

```bash
# Run tests in isolated container
docker-compose -f docker-compose-tests.yml up --build test_runner

# Run specific test suite in container
docker-compose -f docker-compose-tests.yml exec test_runner pytest src/tests/unit/ -v
```

### ✅ Test Categories

| Test Type       | Location                      | Purpose                      | Coverage                      |
| --------------- | ----------------------------- | ---------------------------- | ----------------------------- |
| **Unit**        | `src/tests/unit/`             | Individual component testing | Functions, methods, utilities |
| **Integration** | `src/tests/test_integration/` | Service interaction testing  | Database, external APIs       |
| **E2E**         | `src/tests/test_e2e/`         | Complete workflow testing    | User journeys, API flows      |
| **Contract**    | `src/tests/doubles/`          | Mock and stub testing        | External dependencies         |

## 🚢 Deployment

### 🔄 Automated CI/CD Pipeline

The project includes a fully automated deployment pipeline using GitHub Actions:

**Triggers:**

- Push to `develop` or `cd-setting` branches
- Pull request merges to these branches
- Manual workflow dispatch

**Pipeline Features:**

- ✅ **Concurrency Control** - Prevents simultaneous deployments
- ✅ **Deployment Locks** - Server-side conflict prevention
- ✅ **Health Checks** - Post-deployment verification
- ✅ **Rollback Support** - Automatic failure recovery
- ✅ **Timeout Protection** - 30-minute deployment limit

### 🔧 GitHub Secrets Configuration

Configure these secrets in your GitHub repository:

1. Go to `Settings → Secrets and variables → Actions`
2. Add the following Repository secrets:

```bash
EC2_HOST=your.server.ip.address          # Production server IP
EC2_USER=ubuntu                          # SSH username
EC2_SSH_KEY=-----BEGIN RSA PRIVATE KEY----- # SSH private key
```

### 🖥️ Manual Deployment

For manual deployment to production server:

```bash
# SSH to production server
ssh ubuntu@your-server-ip

# Navigate to project directory
cd /home/ubuntu/src/online-cinema-project

# Deploy specific branch
bash commands/deploy.sh develop

# Check deployment status
bash commands/check-status.sh
```

### 🏗️ Initial Server Setup

For first-time server configuration:

```bash
# Run automated setup script
ssh ubuntu@your-server-ip
bash /home/ubuntu/src/online-cinema-project/commands/setup-server.sh
```

This script will:

- Install Docker and Docker Compose
- Configure firewall rules
- Set up project directory structure
- Install system dependencies
- Configure environment variables

### 📋 Production Deployment Checklist

Before deploying to production:

- [ ] **SSL Certificates** configured and valid
- [ ] **Firewall Rules** properly configured
- [ ] **Database Backups** strategy implemented
- [ ] **Environment Variables** secured and verified
- [ ] **Domain Configuration** with proper DNS
- [ ] **Monitoring System** active and alerting
- [ ] **Log Rotation** configured for disk management
- [ ] **Security Updates** applied to server
- [ ] **Performance Testing** completed
- [ ] **Backup Recovery** procedure tested

### 🔧 Production Environment Variables

Additional variables for production:

```bash
# Production-specific settings
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=info

# Database connection pooling
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30

# Security settings
SECURE_COOKIES=True
HTTPS_ONLY=True
CORS_ORIGINS=["https://yourdomain.com"]

# Performance settings
WORKERS=4
MAX_CONNECTIONS=1000
KEEPALIVE_TIMEOUT=2
```

## 📊 Monitoring

### 🔍 Health Monitoring

The platform includes comprehensive health monitoring:

```bash
# Run complete health check
bash commands/check-status.sh
```

This script monitors:

- ✅ **Deployment Lock Status** - No conflicting deployments
- ✅ **Docker Container Health** - All services running
- ✅ **Database Connectivity** - PostgreSQL connection
- ✅ **Redis Availability** - Cache and message broker
- ✅ **External Services** - MinIO, MailHog, Nginx
- ✅ **System Resources** - CPU, Memory, Disk usage
- ✅ **Application Logs** - Error detection

### 📈 Service Monitoring Dashboards

| Service           | URL                   | Purpose                            |
| ----------------- | --------------------- | ---------------------------------- |
| **PgAdmin**       | http://localhost:3333 | Database monitoring and management |
| **RedisInsight**  | http://localhost:5540 | Redis monitoring and debugging     |
| **MinIO Console** | http://localhost:9001 | Object storage monitoring          |
| **MailHog**       | http://localhost:8025 | Email delivery monitoring          |

### 🚨 Log Management

```bash
# Application logs
docker-compose logs -f web

# Database logs
docker-compose logs -f postgres_theater

# Background task logs
docker-compose logs -f celery_worker_theater

# Reverse proxy logs
docker-compose logs -f nginx

# All service logs
docker-compose logs -f
```

### 📊 Performance Metrics

Monitor key performance indicators:

- **Response Times** - API endpoint performance
- **Database Queries** - Query execution time
- **Memory Usage** - Container resource consumption
- **Disk Space** - Database and file storage
- **Network Traffic** - Request/response volumes
- **Error Rates** - Application and system errors

## 🤝 Contributing

### 🔄 Development Workflow

1. **Fork the Repository**

```bash
git clone https://github.com/YOUR_USERNAME/Online-Cinema-Project.git
cd Online-Cinema-Project
```

2. **Create Feature Branch**

```bash
git checkout -b feature/amazing-new-feature
```

3. **Set Up Development Environment**

```bash
poetry install
docker-compose -f docker-compose-dev.yml up -d
```

4. **Make Changes and Test**

```bash
# Run tests
pytest --cov=src

# Check code style
flake8 src/
mypy src/

# Format code (if using)
black src/
isort src/
```

5. **Commit and Push**

```bash
git add .
git commit -m "feat: add amazing new feature"
git push origin feature/amazing-new-feature
```

6. **Create Pull Request**

- Open PR against `develop` branch
- Include description of changes
- Ensure all tests pass
- Request code review

### 📝 Code Standards

- **Type Hints**: Use Python type hints throughout
- **Docstrings**: Document all public functions and classes
- **Testing**: Write tests for new functionality
- **Coverage**: Maintain >80% test coverage
- **Style**: Follow PEP 8 with flake8 configuration
- **Async**: Use async/await patterns for I/O operations

### 🧪 Testing Requirements

- Write unit tests for business logic
- Include integration tests for database operations
- Add E2E tests for API endpoints
- Mock external service dependencies
- Test error conditions and edge cases

### 📋 Pull Request Guidelines

- **Clear Description**: Explain what and why
- **Small Changes**: Keep PRs focused and reviewable
- **Tests Included**: All new code must have tests
- **Documentation**: Update README/docs if needed
- **No Breaking Changes**: Maintain backward compatibility

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Online Cinema Project Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 👥 Authors & Contributors

- **Yurii Okal** - _Initial development_ - [yurii.okal@mate.com](mailto:yurii.okal@mate.com)
- **iSevenpwnz** - _Current maintainer_ - [GitHub Profile](https://github.com/iSevenpwnz)

## 🙏 Acknowledgments

- [**FastAPI**](https://fastapi.tiangolo.com/) for the excellent async web framework
- [**SQLAlchemy**](https://sqlalchemy.org/) for the powerful ORM capabilities
- [**Pydantic**](https://pydantic-docs.helpmanual.io/) for data validation excellence
- [**Docker**](https://docker.com/) for containerization simplicity
- [**PostgreSQL**](https://postgresql.org/) for robust database foundation
- [**Redis**](https://redis.io/) for caching and message broker capabilities
- **Python Community** for continuous innovation and support

---

<div align="center">

**🎬 Built with ❤️ for the Developer Community 🚀**

_Star ⭐ this repository if you find it helpful!_

[⬆ Back to Top](#-online-cinema-platform)

</div>
