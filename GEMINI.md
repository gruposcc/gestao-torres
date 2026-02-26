# Project: really-aio

## Project Overview

This is a web application named `really-aio`, designed to manage real estate properties, clients, and contracts. It features a robust backend built with Python using the FastAPI framework, SQLAlchemy for ORM, and PostgreSQL as the database. Key functionalities include user authentication (supporting JWT, Argon2, Passlib, and LDAP), geolocation services (using GeoAlchemy2 and Geopy), and real-time notifications via Server-Sent Events (SSE). The frontend integrates Alpine.js and htmx.org for dynamic user interfaces, with styling provided by TailwindCSS and DaisyUI. The project utilizes Docker for easy setup and orchestration of its PostgreSQL database.

## Technologies Used

*   **Backend:** Python 3.14+, FastAPI, SQLAlchemy, Alembic, Uvicorn, Asyncpg, GeoAlchemy2, Geopy, Jinja2, LDAP3, Passlib, PyJWT, Argon2.
*   **Frontend:** Alpine.js, htmx.org, TailwindCSS, DaisyUI, Esbuild.
*   **Database:** PostgreSQL, PostGIS (inferred from GeoAlchemy2).
*   **Containerization:** Docker, Docker Compose.
*   **Package Management:** `uv` (Python), `pnpm` (JavaScript).
*   **Development Tools:** Nodemon, Concurrently.

## Building and Running

This project uses `uv` for Python dependency management and `pnpm` for JavaScript dependencies. Ensure both are installed before proceeding.

### 1. Setup Environment Variables

Copy the example environment file and populate it with your specific configurations:

```bash
cp .env.example .env
# Edit .env with your database credentials, JWT secret, etc.
```

### 2. Database Setup

The project uses Docker Compose to run a PostgreSQL database.

```bash
docker-compose up -d postgres
```

### 3. Install Dependencies

Install Python dependencies using `uv`:

```bash
uv sync
```

Install JavaScript dependencies using `pnpm`:

```bash
pnpm install
```

### 4. Database Migrations

Apply database migrations using Alembic:

```bash
uv run --env-file .env alembic upgrade head
```

If you need to create a new migration (e.g., after model changes):

```bash
uv run --env-file .env alembic revision --autogenerate -m "Your migration message"
```

### 5. Running the Application

**Full Development Mode (Frontend & Backend):**

This command runs both the frontend build/watch processes and the backend Uvicorn server in parallel.

```bash
make dev-full
```

**Backend Only (Development Mode):**

Runs the FastAPI application with Uvicorn, including auto-reloading on code changes.

```bash
make dev
```

**Frontend Builds (Manual):**

*   Build CSS: `pnpm run build.css`
*   Build JavaScript: `pnpm run build.js`

### 6. Create Superuser

To create an administrator user for the application:

```bash
make create_superuser
```

## Development Conventions

*   **Python Structure:** Follows a standard FastAPI project layout with distinct directories for `models`, `schemas`, `routes`, `services`, `dependencies`, and `core` utilities.
*   **Frontend Development:** Relies heavily on HTMX for server-rendered HTML and Alpine.js for client-side interactivity. TailwindCSS and DaisyUI are used for a consistent and efficient styling approach.
*   **Configuration:** All sensitive and environment-specific settings are managed via environment variables loaded from a `.env` file.
*   **Database Migrations:** Alembic is used for managing database schema changes. New migrations should be generated with `alembic revision --autogenerate`.
*   **Scripting:** Utility scripts for development tasks (like `dev.py` and `create_superuser.py`) are located in the `scripts/` directory.
