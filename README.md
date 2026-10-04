# Videoflix Backend

Backend API for the Videoflix video streaming application.

The project is built with Django and Django REST Framework. It provides
user registration, email activation, JWT authentication, password reset,
video metadata, HLS streaming and asynchronous video processing.

## Technologies

- Python
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Django RQ
- Simple JWT
- FFmpeg
- Docker
- Docker Compose

## Features

### Authentication

Users authenticate with their email address.

New accounts are inactive after registration and must be activated using
an activation link.

Authentication uses JWT access and refresh tokens stored in HTTP-only
cookies.

Available authentication endpoints:

- `POST /api/register/`
- `GET /api/activate/<uidb64>/<token>/`
- `POST /api/login/`
- `POST /api/logout/`
- `POST /api/token/refresh/`
- `POST /api/password_reset/`
- `POST /api/password_confirm/<uidb64>/<token>/`

### Video API

Authenticated users can retrieve the available videos using:

`GET /api/video/`

The response contains the metadata required by the Videoflix frontend,
including title, description, category and thumbnail URL.

### HLS Streaming

Videos are streamed using HTTP Live Streaming.

Available resolutions:

- 480p
- 720p
- 1080p

Playlist endpoint:

`GET /api/video/<video_id>/<resolution>/index.m3u8`

Segment endpoint:

`GET /api/video/<video_id>/<resolution>/<segment>.ts`

HLS playlists and segments require authentication.

### Background Processing

Uploaded videos are processed asynchronously.

Django RQ sends video processing jobs to Redis. The RQ worker uses
FFmpeg to create HLS streams in the supported resolutions.

## Environment Variables

Copy `.env.example` and create a local `.env` file.

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