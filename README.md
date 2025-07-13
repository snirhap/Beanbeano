☕️ Beanbeano — Home Brew Coffee Review API

A Python Flask API that lets home brewers review and rate coffee beans, track brew methods, and analyze roaster quality. Built with modular, testable design and designed for easy scaling, observability, and CI/CD integration.

---

## 🚀 Features

- 📝 Users can submit reviews of beans they've brewed at home
- ⚙️ Tracks brew method (e.g. V60, Aeropress) and drink type (e.g. espresso, milk-based)
- 📊 Roaster-level scoring based on average bean ratings
- 🔐 JWT-based authentication for review submission
- 📦 Modular Flask blueprint architecture
- ✅ Unit and integration tests using `pytest`
- 🧪 CI-ready with GitHub Actions (coming soon)
- 🐳 Docker support for local development

---

## 📦 Tech Stack

- **Python 3.11**
- **Flask** + Flask Blueprints
- **SQLAlchemy** ORM
- **PostgreSQL**
- **Docker**
- **JWT Auth (Flask-JWT-Extended)**
- **Pytest** for testing
- **GitHub Actions** for CI (planned)

---

## 🛠️ Getting Started

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized dev)
- PostgreSQL (or use the SQLite fallback)

### Setup

Clone the repo:

```bash
git clone https://github.com/snirhap/Beanbeano.git
cd Beanbeano
```

### Virtual Env (for local flask run)
Create a virtual environment and install dependencies:

```python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Create .env file:
```
DATABASE_URL=postgresql://postgres:postgres@db:5432/beanbeanodb
JWT_SECRET_KEY=supersecretkey
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=beanbeanodb
APP_PORT=8000
```

### Run the server:
``` 
docker-compose up --build --scale web=3
```

### Run unit tests with:
```
pytest
```