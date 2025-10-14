# FreJun Virtual Workspace Booking API

This is a RESTful API for a simplified "Virtual Workspace Room Booking System", built with Python, Django REST Framework, and PostgreSQL. The entire application is containerized with Docker for easy setup and deployment.

## Features

* **Room Availability:** Check for available rooms for a given time slot.
* **Booking Management:** Create and cancel room bookings with priority-based logic.
* **Concurrency Safe:** Uses database transactions to prevent race conditions during booking.
* **Paginated Lists:** The endpoint for listing all bookings is paginated for efficiency.
* **Automated Tests:** Includes a comprehensive test suite to ensure code reliability.
* **Interactive API Docs:** Auto-generates a Swagger/OpenAPI documentation page.

## Tech Stack

* **Backend:** Python, Django, Django REST Framework
* **Database:** PostgreSQL
* **Containerization:** Docker, Docker Compose
* **API Documentation:** `drf-spectacular` (Swagger/OpenAPI)

## Getting Started

### Prerequisites

* Docker
* Docker Compose

### Setup & Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/frejun-booking-api.git](https://github.com/your-username/frejun-booking-api.git)
    cd frejun-booking-api
    ```

2.  **Build and run the Docker containers in the background:**
    ```bash
    docker compose build
    docker compose up -d
    ```

3.  **Apply the database migrations:**
    This command sets up the database schema and seeds it with the 15 initial rooms.
    ```bash
    docker compose exec web python manage.py migrate
    ```

The API server is now running and accessible at `http://localhost:8000`.

## API Documentation

Once the application is running, the interactive Swagger UI documentation is available at:

[**http://localhost:8000/api/docs/**](http://localhost:8000/api/docs/)

## Running the Automated Tests

To run the complete test suite, use the following command:

```bash
docker compose exec web python manage.py test
```

## API Endpoint Examples

*(Note: The base URL is `http://localhost:8000`)*

### 1. Check Available Rooms

* **Endpoint:** `GET /api/v1/rooms/available/`
* **Query Parameters:**
    * `start_time` (ISO 8601 format, e.g., `2025-11-20T10:00:00Z`)
    * `end_time` (ISO 8601 format, e.g., `2025-11-20T11:00:00Z`)
* **Example `curl`:**
    ```bash
    curl "http://localhost:8000/api/v1/rooms/available/?start_time=2025-11-20T10:00:00Z&end_time=2025-11-20T11:00:00Z"
    ```

### 2. Create a Booking

* **Endpoint:** `POST /api/v1/bookings/`
* **Body (JSON):**
    ```json
    {
        "start_time": "2025-11-20T10:00:00Z",
        "end_time": "2025-11-20T11:00:00Z",
        "booking_type": "individual"
    }
    ```

### 3. List All Bookings

* **Endpoint:** `GET /api/v1/bookings/`
* **Example `curl`:**
    ```bash
    curl "http://localhost:8000/api/v1/bookings/"
    ```

### 4. Cancel a Booking

* **Endpoint:** `POST /api/v1/cancel/{booking_id}/`
* **Example `curl`:**
    ```bash
    curl -X POST http://localhost:8000/api/v1/cancel/a1b2c3d4-e5f6-..../
    ```

## Assumptions Made

* **Simplified Authentication:** For the purpose of this take-home challenge, user authentication is simplified. All bookings are attributed to a single, auto-created 'testuser'. In a production environment, a proper token-based authentication system (like JWT) would be implemented to identify the user making the request.
* **Shared Desk Logic:** The business rule "Shared desks are auto-filled by individuals until full" has been simplified. The current logic books the entire shared desk for one individual. A more complex implementation would be required to track individual slots within each shared desk.