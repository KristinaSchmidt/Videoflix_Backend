# Videoflix Backend

Videoflix is a Django REST Framework backend for a video streaming
application.

The backend provides user registration, email activation, JWT
authentication, password reset, video metadata, HLS streaming and
asynchronous video processing.

## Technologies

- Python 3.13
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Django RQ
- Simple JWT
- FFmpeg
- Docker
- Docker Compose

## Requirements

For the recommended setup only the following software is required:

- Git
- Docker Desktop with Docker Compose

Python, PostgreSQL, Redis and FFmpeg do not have to be installed
separately when the project is started with Docker.

## Project Setup

### 1. Clone the repository

```bash
git clone https://github.com/KristinaSchmidt/Videoflix_Backend.git
cd Videoflix_Backend
```

### 2. Create the environment file

The repository contains an `.env.example` file with all required
environment variables.

Create your local `.env` file from it.

Git Bash / Linux / macOS:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

The `.env` file contains sensitive configuration and is therefore
excluded from Git.

### 3. Configure the environment variables

The database and Redis host names must remain `db` and `redis` when
using Docker Compose because these are the service names inside the
Docker network.

Example:

```env
SECRET_KEY=change-me
DEBUG=True

POSTGRES_DB=videoflix
POSTGRES_USER=videoflix
POSTGRES_PASSWORD=videoflix
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

FRONTEND_URL=http://127.0.0.1:5500
```

## Email Configuration

Videoflix sends emails for account activation and password reset.

For real email delivery, configure an SMTP server in `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@example.com
```

Replace the example SMTP values with the credentials supplied by your
email provider.

`DEFAULT_FROM_EMAIL` defines the sender address used for activation and
password reset emails.

For local development without a real SMTP account, the console email
backend can be used:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@videoflix.local
```

With the console backend, emails are not delivered to a mailbox.
Instead, their content and the activation or password-reset link are
printed in the backend container logs.

The logs can be displayed with:

```bash
docker compose logs -f web
```

## Start the Project

Make sure Docker Desktop is running.

Build the images and start all services:

```bash
docker compose up --build -d
```

Docker Compose starts:

- PostgreSQL
- Redis
- Django web server
- Django RQ worker

The database and Redis services have health checks. The web application
and worker wait until the required services are available.

The `backend.entrypoint.sh` script additionally waits for PostgreSQL and
runs the Django database migrations automatically before the application
starts.

The backend is then available at:

`http://127.0.0.1:8000/`

## Check Running Containers

```bash
docker compose ps
```

The database and Redis containers should be shown as healthy and the
web and rqworker containers should be running.

## Django System Check

```bash
docker compose exec web python manage.py check
```

A successful result is:

```text
System check identified no issues (0 silenced).
```

## Database Migrations

Migrations are automatically executed by the backend entrypoint when
the containers start.

They can also be executed manually:

```bash
docker compose exec web python manage.py migrate
```

After changing models, create migrations with:

```bash
docker compose exec web python manage.py makemigrations
```

## Create an Admin User

```bash
docker compose exec web python manage.py createsuperuser
```

The Django administration interface is available at:

`http://127.0.0.1:8000/admin/`

## Run Tests

Run the complete test suite inside the Docker container:

```bash
docker compose exec web python manage.py test
```

## Stop the Project

```bash
docker compose down
```

To remove the containers and Docker volumes including the local
PostgreSQL data:

```bash
docker compose down -v
```

## Authentication API

Users authenticate with their email address.

New accounts are inactive after registration and have to be activated
through the activation link sent by email.

JWT access and refresh tokens are stored in HTTP-only cookies.

Available endpoints:

- `POST /api/register/`
- `GET /api/activate/<uidb64>/<token>/`
- `POST /api/login/`
- `POST /api/logout/`
- `POST /api/token/refresh/`
- `POST /api/password_reset/`
- `POST /api/password_confirm/<uidb64>/<token>/`

## Video API

Authenticated users can retrieve the available videos with:

```text
GET /api/video/
```

The response contains the video metadata required by the Videoflix
frontend, including title, description, category and thumbnail URL.

## HLS Streaming

Videos are streamed using HTTP Live Streaming.

Supported resolutions:

- 480p
- 720p
- 1080p

Playlist:

```text
GET /api/video/<video_id>/<resolution>/index.m3u8
```

Segments:

```text
GET /api/video/<video_id>/<resolution>/<segment>.ts
```

HLS playlists and segments require authentication.

## Background Video Processing

Uploaded videos are processed asynchronously.

Django RQ sends processing jobs to Redis. The RQ worker uses FFmpeg to
create HLS streams for the supported resolutions.

## Project Structure

```text
Videoflix_Backend/
├── core/
├── users/
├── videos/
├── backend.entrypoint.sh
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── manage.py
```

## Security

Passwords are stored using Django's password hashing system.

JWT authentication tokens are stored in HTTP-only cookies.

Password-reset responses do not reveal whether an email address exists.

Secrets and SMTP credentials belong in the local `.env` file. The
`.env` file is excluded from Git and must not be committed.