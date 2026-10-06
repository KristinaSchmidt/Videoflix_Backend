# Videoflix Backend

Videoflix is a Django REST Framework backend for a video streaming
application.

The backend provides user registration, email activation, JWT
authentication, password reset, video metadata, HLS streaming and
asynchronous video processing.

## Technologies

- Python
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Django RQ
- Simple JWT
- FFmpeg
- Gunicorn
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

The repository contains an `.env.template` file with the required
environment variables.

Create your local `.env` file from the template.

Git Bash / Linux / macOS:

```bash
cp .env.template .env
```

Windows PowerShell:

```powershell
Copy-Item .env.template .env
```

The `.env` file contains local configuration and sensitive values and
must not be committed to Git.

Do not remove required environment variables from the template.

### 3. Environment configuration

The Docker setup uses the service names `db` and `redis` internally.
Therefore `DB_HOST` and `REDIS_HOST` should keep these values when the
project is started with Docker Compose.

The environment file also contains the credentials used for the
automatically created Django administrator:

```env
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=adminpassword
DJANGO_SUPERUSER_EMAIL=admin@example.com
```

The Videoflix user model authenticates users by email address. Therefore
the automatically created administrator can log in with the configured
email address and password.

The database configuration uses the following variables:

```env
DB_NAME=videoflix
DB_USER=videoflix
DB_PASSWORD=videoflix
DB_HOST=db
DB_PORT=5432
```

Redis is configured through:

```env
REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
REDIS_PORT=6379
REDIS_DB=0
```

## Email Configuration

Videoflix sends emails for account activation and password reset.

Configure the SMTP settings in `.env`:

```env
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email_user
EMAIL_HOST_PASSWORD=your_email_user_password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=noreply@videoflix.local
```

Replace the example SMTP values with the credentials of the SMTP server
used for the project.

`DEFAULT_FROM_EMAIL` defines the sender address used for activation and
password reset emails.

## Start the Project

Make sure Docker Desktop is running.

Build the backend image and start the services:

```bash
docker compose up --build -d
```

Docker Compose starts:

- PostgreSQL
- Redis
- Videoflix backend

The project uses the provided Docker setup with `backend.Dockerfile`,
`backend.entrypoint.sh` and `docker-compose.yml`.

The backend entrypoint waits until PostgreSQL is available and then
automatically:

1. collects static files
2. creates migrations if necessary
3. applies database migrations
4. creates the configured Django superuser if it does not exist
5. starts the Django RQ worker
6. starts Gunicorn

The RQ worker runs from the backend entrypoint and does not require a
separate Docker Compose service.

The backend is available at:

`http://127.0.0.1:8000/`

## Django Admin

The Django administrator is created automatically when the backend
container starts for the first time.

With the default values from `.env.template`:

```text
Email: admin@example.com
Password: adminpassword
```

The Django administration interface is available at:

`http://127.0.0.1:8000/admin/`

For a real deployment, replace the default administrator credentials
with secure values.

## Check Running Containers

```bash
docker compose ps
```

The PostgreSQL, Redis and backend containers should be running.

## Django System Check

```bash
docker compose exec web python manage.py check
```

A successful result is:

```text
System check identified no issues (0 silenced).
```

## Database Migrations

Migrations are automatically handled by the backend entrypoint when the
container starts.

They can also be executed manually:

```bash
docker compose exec web python manage.py migrate
```

After changing models, migrations can be created with:

```bash
docker compose exec web python manage.py makemigrations
```

## Run Tests

Run the complete test suite inside the backend container:

```bash
docker compose exec web python manage.py test
```

## Stop the Project

Stop the containers with:

```bash
docker compose down
```

To additionally remove the local Docker volumes and local PostgreSQL
data:

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
├── backend.Dockerfile
├── backend.entrypoint.sh
├── docker-compose.yml
├── requirements.txt
├── .env.template
└── manage.py
```

## Security

Passwords are stored using Django's password hashing system.

JWT authentication tokens are stored in HTTP-only cookies.

Password-reset responses do not reveal whether an email address exists.

Secrets, SMTP credentials and production passwords belong in the local
`.env` file. The `.env` file is excluded from Git and must not be
committed.