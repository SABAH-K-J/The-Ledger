# The Ledger Microservices

This repository contains "The Ledger," a microservices-based application demonstrating secure authentication and role-based access control (RBAC) using Python and FastAPI.

## Architecture

The system is composed of three interconnected services:

1. **Auth Service (`auth_service`)**: 
   - Manages user authentication and identity.
   - Uses SQLite and `passlib` for secure password hashing.
   - Issues JSON Web Tokens (JWT) signed with a private RSA key.
2. **Ledger Service (`ledger_service`)**: 
   - The core business logic service managing financial transactions.
   - Uses SQLAlchemy and SQLite.
   - Requires valid JWT tokens (verified using a public RSA key) to access endpoints.
   - Implements RBAC: regular members can create deposits, but only `head` roles can view and verify pending approvals.
3. **Protected Service (`protected_service`)**: 
   - A demonstration service showing how to securely protect endpoints.
   - Implements strict RBAC (e.g., an `/admin-only` endpoint restricted to `admin` roles).

## Technologies Used

* **Framework**: FastAPI
* **Database**: SQLite with SQLAlchemy ORM
* **Authentication**: JWT (JSON Web Tokens) with RSA Asymmetric Keys (RS256)
* **Containerization**: Docker & Docker Compose
* **Security**: Passlib (Bcrypt) for password hashing

## Getting Started

### Prerequisites
* [Docker](https://www.docker.com/) and Docker Compose.
* OpenSSL (to generate the cryptographic keys).

### Generating Cryptographic Keys
Since the private and public keys are excluded from version control for security, you must generate them locally before running the application:

```bash
mkdir -p keys
openssl genrsa -out keys/private.pem 2048
openssl rsa -in keys/private.pem -outform PEM -pubout -out keys/public.pem
```
### Running the Application

To start the entire microservices stack, simply run:

```bash
docker-compose up --build
```

This will build the images and start the services on the following ports:
* **Auth Service**: `http://localhost:8001`
* **Ledger Service**: `http://localhost:8002`
* **Protected Service**: `http://localhost:8003`

*(Note: The databases are automatically seeded on startup with test users: `johndoe` (admin), `bob` (member), `alice` (head), `charlie` (admin). The passwords match the usernames + `123` (e.g., `bob123`).)*

## Testing the Flow

1. **Login**: Send a `POST` request to `http://localhost:8001/login` with `{"username": "bob", "password": "bob123"}` to receive a JWT.
2. **Deposit**: Send a `POST` request to `http://localhost:8002/deposit` with `{"amount": 100}` and set the `Authorization: Bearer <your_token>` header.
3. **Verify**: Login as `alice` (head), and send a `GET` request to `http://localhost:8002/approvals` to see Bob's pending transaction.
