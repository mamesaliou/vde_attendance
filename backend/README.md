# VDE Attendance - Backend

Application FastAPI pour la gestion des présences scolaires.

## Installation

```bash
# Cloner le projet
git clone https://github.com/ALYCIS/vde_attendance.git
cd vde_attendance/backend

python -m venv venv
venv\Scripts\activate

pip install uv

uv sync

cp .env.example .env
uv run alembic upgrade head

uv run main.py
```

## Docker

```bash
docker-compose up -d
```

## API

- **API** : http://localhost:8000
- **Documentation** : http://localhost:8000/docs
- **PostgreSQL** : localhost:5433
