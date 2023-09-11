# BillEase

Brief project description.

## Table of Contents

- [Create Virtual Environment](#create-virtual-environment)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Running Migrations](#running-migrations)
- [Run the Application](#run-the-application)

## Create Virtual Environment

1. Create a virtual environment using Python 3:

    ```bash
    python3 -m venv venv
    ```

2. Activate the virtual environment:

    On macOS and Linux:
    ```bash
    source venv/bin/activate
    ```

    On Windows:
    ```bash
    venv\Scripts\activate
    ```

## Installation

1. Install the required packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

## Database Setup

1. Initialize Alembic for database migrations:

    ```bash
    alembic init alembic
    ```

2. Edit the `alembic.ini` file:

    Set the following configurations:

    ```ini
    script_location = alembic
    sqlalchemy.url = postgresql://user:password@localhost/dbname
    ```

3. In the `alembic/env.py` file, configure Alembic to use your application's database models:

    ```python
    from models.models import Base
    target_metadata = Base.metadata
    ```

## Running Migrations

1. Generate an automatic migration script:

    ```bash
    alembic revision --autogenerate -m "create-user-table"
    ```

2. Apply the migrations to the database:

    ```bash
    alembic upgrade head
    ```

## Run the Application

1. Run the application using Python:

    ```bash
    python3 main.py
    ```

   Or, if using UVicorn:

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 3000 --reload
    ```

# Seed Data

This section provides instructions on how to seed data for your project.

1. Get into the seeders folder:

   Use the `cd` command to navigate to the `seeders` folder where the seed data is located.


    ```bash
    cd seeders
    ```

2. Run the seeders.py file:

    ```bash
    python3 seed_users.py
    ```