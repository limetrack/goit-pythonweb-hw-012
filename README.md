# FastAPI App with PostgreSQL, Redis (Koyeb, Docker & Local Setup)

## Main features added in v12:  
- Sphinks docs  
- unit tests for repositories  
- integrational tests for routes  
- redix cache  
- reset password flow  
- role system (user, admin)  
- refresh token  

## Deployed to Koyeb
[Link](https://cognitive-ginnifer-k-university-d3b4cf00.koyeb.app/docs)  
- Main app & Postgress DB -> Koyeb  
- Redis -> Upstash

## Prerequisites
Python 3.12+
Poetry (for dependency management)
Docker & Docker Compose (for running PostgreSQL)

## Setup & Running the App

### Clone the Repository
```git clone https://github.com/goit-pythonweb-hw-12.git```
```cd goit-pythonweb-hw-12```

### Install Dependencies
```poetry install```

### Setup the Environment Variables
Copy the .env.example file and rename it to .env:
```cp .env.example .env```
Edit the .env file and set the correct database credentials.

### Run Full App with Docker (Backend + DB)
```docker-compose up --build -d```

### Run migrations
```docker-compose exec backend poetry run alembic upgrade head```

### Stop Docker Services
```docker-compose down```

## Run PostgreSQL in Docker (without the app)
If you want to run only the database in Docker:
```docker run --name my_local_postgres -e POSTGRES_USER=myuser -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=mylocaldb -p 5432:5432 -d postgres:15```

## Running the App (Without Docker)
If you prefer to run the app locally without Docker:
### Start PostgreSQL Locally
Ensure PostgreSQL is running locally and update .env with:

```DATABASE_URL=postgresql+asyncpg://myuser:mypassword@localhost:5432/mylocaldb```

### Apply Database Migrations

```USE_LOCAL_DB=true poetry run alembic upgrade head```

### Run the FastAPI App
```USE_LOCAL_DB=true poetry run uvicorn main:app --reload```
