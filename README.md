# Deals Bot

## Project Overview
The Deals Bot is designed to help users find and track the latest deals, sending notifications directly to users via Telegram. Users can register on the website to manage their tracked deals and stay up-to-date. The bot fetches deal data from [Marktguru](https://www.marktguru.de/) to ensure the latest offers are always available.

## Tech Stack
The project is powered by the following technologies:

- **Python**: The core programming language for backend logic.
- **Django**: A high-level Python web framework that enables rapid development and clean, pragmatic design.
- **Celery**: An asynchronous task queue used to handle background jobs and real-time tasks.
- **RabbitMQ**: The message broker that Celery uses to manage task queues.
- **Redis**: An in-memory data structure store used for caching and enhancing task performance.

## Features
- **Automated Deal Scraping**: Fetches deals from [Marktguru](https://www.marktguru.de/) at regular intervals.
- **Telegram Notifications**: Sends messages with the latest deals directly to users on Telegram.
- **User Registration and Profile Management**: Users can register on the website to manage their account and tracked deals.
- **Personal Deal Tracking**: Each user has a personalized list of tracked deals, viewable on the website.
- **Real-time Processing**: Celery and RabbitMQ power asynchronous processing, enabling real-time deal fetching and notifications.
- **Caching**: Redis is used to cache data, speeding up response times.

## Getting Started

### Prerequisites
Make sure you have the following installed on your system:
- Python 3.8 or higher
- RabbitMQ
- Redis

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/deals-bot.git
    cd deals-bot
    ```

2. **Install dependencies:**
    Create a virtual environment and install project dependencies.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. **Set up RabbitMQ and Redis:**
   - Follow the [RabbitMQ installation guide](https://www.rabbitmq.com/download.html).
   - Install Redis by following the [Redis installation instructions](https://redis.io/download).

4. **Environment Variables**:
    Create a `.env` file in the root directory and add necessary environment variables, including:
    - **Database credentials**
    - **Telegram bot token**
    - **API keys for Marktguru**

### Running the Application

1. **Start the Django server:**
    ```bash
    python manage.py runserver
    ```

2. **Run Celery Worker:**
    ```bash
    celery -A your_project_name worker -l info
    ```

3. **Run Celery Beat (for scheduled tasks):**
    ```bash
    celery -A your_project_name beat -l info
    ```

### Running Tests
To run tests for the application, use:
```bash
python manage.py test
