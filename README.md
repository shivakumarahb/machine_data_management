# Data Management System

This repository consists of two main components: a data generator with a modular database schema and a Django REST Framework (DRF) application for user management and API endpoints to interact with the generated data.

## Table of Contents
- [Part 1: Data Generator and Database Schema](#part-1-data-generator-and-database-schema)
  - [Script Functionality](#script-functionality)
  - [Database Schema](#database-schema)
- [Part 2: DRF API Application](#part-2-drf-api-application)
  - [Endpoints](#endpoints)
  - [WebSocket for Real-time Machine Data](#websocket-for-real-time-machine-data)
- [How to Run](#how-to-run)
  - [Requirements](#requirements)
  - [Setup](#setup)

## Part 1: Data Generator and Database Schema

### Folder Structure
  

                    ├──data_generator_and_db_schema
                        ├── create_schema.py
                        ├── db_schema.txt
                        └── generator.py

### Script Functionality

The purpose of this part is to generate machine and axis data, values at specified intervals, and storing the data in a database. The values generated adhere to the structure outlined in an external Excel file specifying the "UPDATE INTERVAL" for each field.

- **generator.py**: This script:
  - Generates data for **20 machines**.
  - Each machine contains **5 axes (X, Y, Z, A, C)**.
  - The data is generated at specified intervals and includes attributes such as `actual_position`, `target_position`, `velocity`, and `acceleration` for each axis.
  - The script writes these values to the database via SQL queries.

- **create_schema.py**: This script:
  - Defines and creates a modular database schema for storing machine, axis, and tool data.
  - The schema allows for easy scaling, such as adding new machines, axes, or fields without breaking existing data.
  
### Database Schema
The database is designed to be **modular and scalable**. Below is a brief overview of the schema:

- **machine**: Stores information about machines (e.g., machine name, tool capacity).
- **tool**: Stores tool-specific data for each machine.
- **tool_usage**: Records which tool is in use for each machine.
- **axis**: Each machine has multiple axes (X, Y, Z, A, C), each with its own max velocity, max acceleration, etc.
- **axis_data**: Tracks dynamic axis data like position, velocity, and acceleration, including computed fields such as `distance_to_go`.

The schema allows to add more machines, axes, and other fields in the future without breaking the design.

                                    machine ────< tool
                                    │
                                    │
                                    └───< tool_usage
                                    │
                                    └───< axis ────< axis_data

## Part 2: DRF API Application

This part provides a **Django REST Framework (DRF)**-based API for user management and interaction with the generated machine data. It includes token-based authentication and provides several CRUD operations.

### Folder Structure

                    ├── drf_api_app
                    │   ├── data_management_system
                    │   ├── manage.py
                    │   └── user_management


### Endpoints

This part of the application provides the following key functionalities:

1. **User Management with Token-based Authentication:**
   - Register new users.
   - Login and obtain an authentication token.
   - Manage user authentication and authorization.
   - adding users to diffrent goups such as Manager, Supervisor, Operator etc

2. **CRUD operations for Schema:**
   - Create, retrieve, update, and delete data for the machine schema defined in Part 1.
   - Endpoints to manage machines, axes, and their corresponding data.

3. **Machine Historical Data:**
   - Fetch machine data for a specific axis or multiple axes for the past 15 minutes.
   - Query historical data for any combination of machines and axes.

4. **Real-time Machine Data with WebSocket:**
   - Establish a WebSocket connection to retrieve real-time updates on machine values such as axis positions, velocity, and more.

### WebSocket for Real-time Machine Data

The API provides WebSocket support to allow clients to subscribe and receive real-time updates on the machine's status (axis data, tool data, etc.).

- The WebSocket connection pushes updated values for all machines and axes in real-time.
- This feature enables monitoring and quick response to changes in machine states.

## How to Run

### Requirements
- Python 3.10+
- Django
- Django REST Framework
- PostgreSQL (for database setup)
- Channels (for WebSocket functionality)

### Setup

1. **Set up PostgreSQL Database**:
    ```
    Create a PostgreSQL database for storing the machine data.
    Update the database settings in drf_api_app/data_management_system/settings.py with your database credentials.
    ```


2. **Clone the Repository**:
   ```bash
   git clone git@github.com:shivakumarahb/machine_data_management.git
   cd machine_data_management/drf_api_app
   python manage.py migrate
   ```

3. **Run Data Generator**:

    This part generates machine and axis data, and pushes it to the database:
    ```bash
    cd data_generator_and_db_schema
    python3 create_schema.py  # Create the database schema
    python3 generator.py      # Generate and push machine data
    ```

4. **Run the DRF API Application**:

    After setting up the database and data generation, you can run the DRF API
    ```bash
    cd ../drf_api_app
    python3 manage.py runserver
    ```

5. **Accessing the API**:

    Once the DRF API application is running, you can access the endpoints at:

    ```bash
    Available Endpoints
    The API provides the following endpoints for user management and data retrieval:

    User Registration: POST /register/

    adding user to group : POST /add-user-to-group/

    Admin Site: GET /admin/

    OAuth2 Authentication: GET /o/

    following endpoints for CRUD operations:

    Machine

    GET /data/machines/ #List all machines
    POST /data/machines/ #Create a new machine
    GET /data/machines/{id}/ #Retrieve a machine by ID
    PUT /data/machines/{id}/ #Update a machine by ID
    DELETE /data/machines/{id}/ #Delete a machine by ID

    Tool

    GET /data/tools/
    POST /data/tools/
    GET /data/tools/{id}/
    PUT /data/tools/{id}/
    DELETE /data/tools/{id}/

    Tool Usage

    GET /data/tool-usage/
    POST /data/tool-usage/
    GET /data/tool-usage/{id}/
    PUT /data/tool-usage/{id}/
    DELETE /data/tool-usage/{id}/

    Axis

    GET /data/axes/
    POST /data/axes/
    GET /data/axes/{id}/
    PUT /data/axes/{id}/
    DELETE /data/axes/{id}/

    Axis Data

    GET /data/axises/
    POST /data/axises/
    GET /data/axises/{id}/
    PUT /data/axises/{id}/
    DELETE /data/axises/{id}/

    # for last 15 mins of axis data 
     POST /api/axis-data


    #for websocket connection run server in the app directory by below command and connect by client using token 
    uvicorn data_management_system.asgi:application --host 0.0.0.0 --port 8100 



    ```