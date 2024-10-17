# Library-Service-Project

Library Service Project designed to provide a management system for book borrowings. 
This API can be used to: create profiles, books, add borrowing/return books, 
getting automatic notification on telegram about borrowings and payments, Stripe payments integration.

## Table of Contents

- [Features](#features)
- [Database structure](#Database-structure)
- [Installation](#installation)
- [Run with Docker](#Run-with-Docker)

## Features:

- User registration and login with email
- Manage books and books borrowing
- JWT authentication support
- Filter active borrowings and borrowings by users
- Send notifications about payments and overdue borrowings
- Allow users to make payments for borrowed books or fines
- Support payment session status tracking and renew payment session
- Provide payment session URLs and IDs for processing
- API documentation

## Database structure

![Database structure](demo_screenshots/db_structure.png)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/V-Shkrobatskyi/Library-Service-Project.git
   cd Library-Service-Project
   python -m venv venv
   venv\Scripts\activate (on Windows)
   source venv/bin/activate (on macOS)
   pip install -r requirements.txt
   ```
2. Copy .env_sample -> env. and populate with required data:
   ```
   POSTGRES_HOST=POSTGRES_HOST
   POSTGRES_PORT=POSTGRES_PORT
   POSTGRES_NAME=POSTGRES_NAME
   POSTGRES_USER=POSTGRES_USER
   POSTGRES_PASSWORD=POSTGRES_PASSWORD
   PGDATA=/var/lib/postgresql/data
   
   SECRET_KEY=SECRET_KEY
   
   TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID
   
   CELERY_BROKER_URL=CELERY_BROKER_URL
   CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND
   
   STRIPE_SECRET_KEY=STRIPE_SECRET_KEY
   ```
   [How to get Telegram chat bot token read docs here.](https://core.telegram.org/bots/features#botfather)

   How to get "Telegram chat id":
      - go to web telegram version
      - start new group and add your bot there
      - in group url "Telegram chat id" is after symbol #

3. Run database migrations and start server:
    ```
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
    ```

## Run with Docker

Docker should be installed.

1. Pull docker container:
   ```
   docker pull vitaliitestaccount/library-service-project
   ```
2. Run docker container
   ```
    docker-compose build
    docker-compose up
   ```
