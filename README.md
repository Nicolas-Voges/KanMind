# KanMind (Backend)

Backend for the KanMind application — a Kanban-style task management API built with Django and Django REST Framework. This is the backend-only repository; no frontend is included.

## Table of Contents

- [Overview](#overview)  
- [Features](#features)  
- [Requirements](#requirements)  
- [Setup & Installation](#setup--installation)  

## Overview

KanMind provides a RESTful API for managing boards, tasks, and comments in a Kanban-style workflow. The backend is built with Django and Django REST Framework (DRF) and supports:

- User registration, login, and token-based authentication  
- Board creation, updates, deletion, and membership-based access control  
- Task creation, editing, assignment, and status tracking  
- Commenting on tasks with validation and permission checks  

## Features

- **Token-based Authentication** via Django REST Framework's authtoken  
- **Role-based permissions**: board owner, board member, task creator, task reviewer  
- **Model validation** to ensure data integrity (e.g., a comment must belong to a task)  
- **Clean and modular structure** with separate apps for authentication (`user_auth_app`) and business logic (`kanban_app`)

## Requirements

- Python 3.8 or higher  
- A virtual environment (recommended)  
- Packages listed in `requirements.txt`

## Setup & Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/Nicolas-Voges/KanMind.git
   cd KanMind

    Set up a virtual environment

python3 -m venv venv
source venv/bin/activate

Install dependencies

pip install -r requirements.txt

Apply migrations

python manage.py migrate

Create a superuser (optional, for admin access)

python manage.py createsuperuser

Run the development server

python manage.py runserver
