# FastAPI Notes API

A RESTful API for managing notes with user authentication, built using **FastAPI**, **SQLAlchemy (Async)**, and **PostgreSQL**.

---

## 🚀 Features

* **User Authentication**: JWT-based authentication with access & refresh tokens
* **Note Management**: Full CRUD operations for notes
* **Search & Filtering**: Advanced search with date ranges and text search
* **Rate Limiting**: Protection against abuse (20 requests/minute)
* **Soft Delete**: Notes are marked as deleted instead of being permanently removed
* **Pagination**: Efficient data retrieval with pagination support
* **API Documentation**: Swagger UI (`/docs`) and ReDoc (`/redoc`)
* **Database Migrations**: Alembic for schema versioning

---

## 📋 Prerequisites

* Python **3.9+**
* PostgreSQL **12+**
* pip (Python package manager)

---

## 🛠 Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/abidkarim74/Notes_CRUD_FastAPI.git
cd Notes_CRUD_FastAPI
```

---

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

---

### 3. Activate the Virtual Environment

**Windows**:

```bash
venv\Scripts\activate
```

**macOS / Linux**:

```bash
source venv/bin/activate
```

---

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root and configure it as follows:

```env
# PostgreSQL (Async SQLAlchemy)
POSTGRES_DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/db_name

# JWT / Token Signing
SIGNER_KEY=dasdasdasdasdklhdhaskdaldlasdjljkjad

# Access & Refresh Token Secrets
ACCESS_SECRET=9xP3mKj7R2vL5sQ8tW1yZ4cF7hN0jM2pO5rT8uX1zB6wV3yG7
REFRESH_SECRET=b6YtV2kL9qP4sR8uW1xZ3cF7hJ0mN2pQ5tS8vY1aD4gH7jK9

# Token Expiry
ACCESS_EXPIRY=60      # Access token expiry (minutes)
REFRESH_EXPIRY=7      # Refresh token expiry (days)
```

⚠️ **Important**:

* Never commit your real `.env` file to version control
* Use strong secrets in production
* Rotate secrets regularly

---

## 🗄 PostgreSQL Setup

```bash
psql -U postgres
```

```sql
CREATE DATABASE db_name;
GRANT ALL PRIVILEGES ON DATABASE db_name TO username;
```

---

## 🔄 Database Migrations (Alembic)

### Initial Setup (First Time Only)

```bash
alembic init migrations
```

Update `alembic.ini`:

```ini
sqlalchemy.url = postgresql://postgres:<password>@localhost:5432/job_db
```

---

### Create Migration

```bash
alembic revision --autogenerate -m "initial migration"
```

---

### Apply Migrations

```bash
alembic upgrade head
```

---

### Rollback Migration

```bash
alembic downgrade -1
```

---

### Useful Alembic Commands

```bash
alembic current
alembic history
alembic heads
alembic revision -m "manual migration"
```

---

## ▶️ Running the Application

### Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🐳 Docker (Optional)

```bash
docker build -t fastapi-notes .
docker-compose up
```

---

## 🧪 Testing

Testing can be performed **manually using Postman or curl**, or via **pytest**.

### Manual Testing (Postman)

* Import OpenAPI schema:

  * `http://localhost:8000/openapi.json`
* Use Authorization header:

```text
Authorization: Bearer <access_token>
```

Postman screenshots are available in the `postman_test_results/` directory.

---

### Manual Testing (curl)

Create a new note:

```bash
curl -X POST "http://localhost:8000/api/notes" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Note", "content": "This is a test note"}'
```

Get all notes:

```bash
curl -X GET "http://localhost:8000/api/notes" \
  -H "Authorization: Bearer <access_token>"
```

---




---

## 📘 API Documentation

Once the app is running:

* **Swagger UI**: `http://localhost:8000/docs`
* **ReDoc**: `http://localhost:8000/redoc`
* **OpenAPI Schema**: `http://localhost:8000/openapi.json`

---

## 📂 Project Structure

```text
project/
├── migrations/
│   ├── versions/
│   └── env.py
├── app/
│   ├── controllers/
│   ├── dependencies/
│   ├── middleware/
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── database/
│   ├── utils/
│   └── server.py
├── .env
├── alembic.ini
└── requirements.txt

```

---

## 🤝 Contributing

1. Create a feature branch
2. Write tests for new functionality
3. Ensure all tests pass
4. Create migrations if needed
5. Submit a pull request

---

## 📄 License

Not availble.
