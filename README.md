# TrampoHub API

A job board (vagas) REST API built with Django, Django REST Framework, and MongoDB, featuring a complete local CI/CD pipeline with Jenkins, SonarQube, and Docker.

This project was built as a hands-on learning exercise to bridge my background in **Java / Spring Boot / Angular** with the **Python / Django** ecosystem, while also practicing DevOps practices I use professionally (Jenkins, SonarQube) in a from-scratch local setup.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running Tests](#running-tests)
- [API Overview](#api-overview)
- [CI/CD Pipeline](#cicd-pipeline)
- [Local Pipeline Infrastructure Setup](#local-pipeline-infrastructure-setup)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | Django 6.0 + Django REST Framework |
| Business data | MongoDB (via MongoEngine ODM) |
| Auth data | SQLite (Django's built-in auth) |
| Authentication | Custom expiring token authentication |
| Testing | pytest, pytest-django, pytest-cov, mongomock, factory_boy |
| Containerization | Docker, Docker Compose (multi-stage builds) |
| CI/CD | Jenkins (Declarative Pipeline) |
| Code quality & security | SonarQube Community Edition |
| Config management | python-decouple (`.env` based) |

> **Note on the database split:** business entities (`Vaga`, `Candidatura`) live in MongoDB, while Django's authentication system (`User`, sessions, tokens) uses the default SQLite backend. This mirrors a common real-world pattern where auth infrastructure and domain data are decoupled.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Jenkins (CI/CD)                        │
│                                                                 │
│  Checkout → Tests (isolated container) → SonarQube → Build →  │
│  Deploy to Homolog                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│  Dev environment    │   │  Homolog environment │   │  SonarQube          │
│  (docker-compose)   │   │  (docker-compose)     │   │  (code quality)     │
│                      │   │                       │   │                     │
│  API :8000           │   │  API :8001            │   │  :9000              │
│  Mongo :27017         │   │  Mongo :27018          │   │                     │
└───────────────────┘   └───────────────────┘   └───────────────────┘
```

Both the development and homologation environments run side-by-side on the same machine, fully isolated from each other via separate Docker Compose project names, ports, and Mongo instances.

---

## Project Structure

```
trampohub-api/
├── vagas/                      # Main Django app
│   ├── models.py                # Vaga, Candidatura (MongoEngine) + Perfil (Django ORM)
│   ├── serializers.py            # DRF serializers
│   ├── views.py                   # ViewSets with custom permissions
│   ├── permissions.py              # IsEmpregador, IsCandidato
│   ├── authentication.py            # Custom expiring token auth
│   └── tests/                        # pytest test suite (50 tests)
├── trampohub_api/
│   └── settings.py                     # Environment-based configuration
├── Dockerfile                            # Multi-stage build (test + production)
├── docker-compose.yml                      # Dev environment
├── docker-compose.homolog.yml                # Homolog environment
├── Jenkinsfile                                 # CI/CD pipeline definition
├── entrypoint.sh                                 # Runs migrations before starting the server
├── requirements.txt                                # Production dependencies
├── requirements-dev.txt                              # Test-only dependencies
└── .env                                                # Local secrets (gitignored)
```

---

## Getting Started

### Prerequisites

- Python 3.14
- Docker Desktop (Windows/WSL2)
- Git

### Local setup

```bash
# Clone the repository
git clone https://github.com/axandrade/trampohub-api.git
cd trampohub-api

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows

# Install dependencies
python -m pip install -r requirements.txt -r requirements-dev.txt

# Create your local .env file (see Environment Variables section)

# Start MongoDB
docker compose up -d

# Run migrations and start the server
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

---

## Environment Variables

Create a `.env` file in the project root (never commit this file):

```
DJANGO_SECRET_KEY=your-generated-secret-key
MONGO_PASSWORD=your-mongo-password
```

Generate a secure Django secret key with:

```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Both variables have safe fallback defaults defined in `settings.py` for test/build environments where the `.env` file isn't present (e.g. inside the Jenkins pipeline container), but a real value is always required for actual dev/homolog usage.

---

## Running Tests

```bash
python -m pytest
```

The test suite (50 tests) uses `mongomock` to simulate MongoDB in-memory, so it runs without requiring a real database connection — fast and fully isolated.

To generate a coverage report:

```bash
python -m pytest --cov=vagas --cov-report=html
```

---

## API Overview

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/api/cadastro/` | Register a new user (Candidato/Empregador) | Public |
| POST | `/api/token/` | Login, returns auth token | Public |
| GET | `/api/vagas/` | List jobs (supports filters) | Authenticated |
| GET | `/api/vagas/?modalidade=Remoto` | Filter by work mode | Authenticated |
| GET | `/api/vagas/?tipo_contrato=CLT` | Filter by contract type | Authenticated |
| GET | `/api/vagas/?localizacao=fortaleza` | Filter by location (partial match) | Authenticated |
| POST | `/api/vagas/` | Create a job posting | Empregador only |
| POST | `/api/candidaturas/` | Apply to a job | Candidato only |
| GET | `/admin/` | Django admin panel | Staff only |

Business rules enforced at the API layer:
- Only users with an **Empregador** profile can create/edit/delete job postings.
- Only users with a **Candidato** profile can apply to jobs.
- A candidate cannot apply to the same job posting twice.

---

## CI/CD Pipeline

The Jenkins pipeline runs the following stages on every manual trigger:

1. **Checkout** — pulls the code from the configured Git branch.
2. **Tests** — runs inside an isolated `python:3.14-slim` Docker agent, installing both production and dev dependencies, then executing the full pytest suite.
3. **SonarQube Analysis** — static code analysis for bugs, code smells, and security vulnerabilities.
4. **Build Docker Image** — multi-stage build; tests run again inside the build itself as a safety gate before the final lightweight image is produced.
5. **Deploy to Homolog** — tears down and recreates the homologation environment with the freshly built image.

Secrets (`DJANGO_SECRET_KEY`, `MONGO_PASSWORD`) are injected via Jenkins credentials at pipeline runtime — never hardcoded, never committed.

```groovy
// Simplified Jenkinsfile structure
pipeline {
    agent any
    stages {
        stage('Checkout') { ... }
        stage('Tests') {
            agent { docker { image 'python:3.14-slim' } }
            environment {
                DJANGO_SECRET_KEY = credentials('django-secret-key')
                MONGO_PASSWORD = credentials('mongo-password')
            }
            steps { sh 'python -m pytest' }
        }
        stage('SonarQube Analysis') { ... }
        stage('Build Docker Image') { ... }
        stage('Deploy to Homolog') { ... }
    }
}
```

---

## Local Pipeline Infrastructure Setup

This project's CI/CD infrastructure runs entirely on a local machine via Docker — there is no external server. Below is a summary of how each piece was provisioned.

### Jenkins

```bash
docker volume create jenkins_home

docker run -d --name jenkins -p 9090:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v //var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts

# Docker CLI + Compose plugin must be installed inside the Jenkins container
docker exec -u root jenkins apt-get update
docker exec -u root jenkins apt-get install -y docker.io curl
docker exec -u root jenkins mkdir -p /usr/libexec/docker/cli-plugins
docker exec -u root jenkins curl -SL \
  https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-x86_64 \
  -o /usr/libexec/docker/cli-plugins/docker-compose
docker exec -u root jenkins chmod +x /usr/libexec/docker/cli-plugins/docker-compose
```

Required Jenkins plugins: **Docker Pipeline**, **SonarQube Scanner**.

### SonarQube

```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:community
```

Jenkins reaches SonarQube via `http://host.docker.internal:9000`, since both run as separate Docker containers on the same host.

### Homolog environment

```bash
docker compose --project-name trampohub-homolog -f docker-compose.homolog.yml up -d
```

Using `--project-name` keeps the homolog stack fully isolated from the dev stack, even though both compose files live in the same directory.

---

## Troubleshooting

A few non-obvious issues encountered while building this pipeline, documented for future reference:

| Symptom | Root cause | Fix |
|---|---|---|
| `Batch scripts can only be run on Windows nodes` | Jenkins container runs Linux internally, even on a Windows host | Use `sh` instead of `bat` in the Jenkinsfile |
| `permission denied ... docker.sock` | Jenkins user lacks access to the mounted Docker socket | `usermod -aG root jenkins` inside the container, then restart |
| `docker: 'compose' is not a docker command` | Debian's `docker.io` package doesn't include Compose | Manually install the Compose CLI plugin binary |
| Homolog container can't reach MongoDB via `localhost` | Containers don't share network namespaces by default | Use Docker Compose service names (e.g. `mongodb`) as the hostname, injected via `MONGO_HOST` env var |
| Two Compose stacks in the same folder kill each other | Docker Compose defaults to folder name as project name | Always pass `--project-name` for the homolog stack |
| `no such table: django_session` on a fresh container | SQLite database is recreated empty on every image build | Run `python manage.py migrate` automatically via an `entrypoint.sh` script |
| SonarQube flags hardcoded `SECRET_KEY` / DB password | Secrets committed directly in `settings.py` | Move to `.env` (local) / Jenkins credentials (CI), with safe non-production fallback defaults |

---

## Roadmap

- [ ] RabbitMQ + Celery for async notifications (e.g. "you received a new application")
- [ ] Angular frontend integration (separate repository: `trampohub-frontend`)
- [ ] JWT-based authentication for the frontend SPA
- [ ] Kubernetes manifests for a more production-like local deployment
- [ ] Parameterized Jenkins builds (branch/commit selection at trigger time)

---

## Author

Built by [Alex Andrade](https://github.com/axandrade) as a personal full-stack learning project, transitioning from a Java/Spring Boot/Angular background into Python/Django.
