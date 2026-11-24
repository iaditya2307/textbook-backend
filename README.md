# textbook-backend

Flask API with MongoDB Atlas for the Folio / textbook frontend.

## Setup (local first, repo later)

1. Create a virtualenv and install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy environment template and fill in your Atlas URI (never commit `.env`):

   ```bash
   cp .env.example .env
   ```

3. Run the server:

   ```bash
   flask --app run:app run --port 5000 --debug
   # or: python run.py
   ```

4. When you're ready for a remote repo:

   ```bash
   git init
   git add .
   git commit -m "Initial Flask backend"
   gh repo create textbook-backend --public --source=. --push
   ```

   You can also create an empty repo on GitHub first, then `git remote add origin ...` and push.

## Environment

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | Atlas connection string (include database name in URI or use `MONGODB_DB_NAME`) |
| `MONGODB_DB_NAME` | Database name (default `textbook`) |
| `FLASK_SECRET_KEY` | Used to sign JWTs |
| `CORS_ORIGINS` | Comma-separated origins (default `http://localhost:3000`) |

## API

| Method | Path | Auth |
|--------|------|------|
| GET | `/health` | No |
| POST | `/api/auth/register` | No |
| POST | `/api/auth/login` | No |
| GET | `/api/books` | Bearer JWT |
| POST | `/api/books` | Bearer JWT |
| GET | `/api/books/<id>` | Bearer JWT |
| PATCH | `/api/books/<id>` | Bearer JWT |
| DELETE | `/api/books/<id>` | Bearer JWT |

Register/login responses include `{ "user": { ... }, "token": "..." }`. Send `Authorization: Bearer <token>` for book routes.

## Indexes

```bash
flask --app run:app ensure-indexes
```