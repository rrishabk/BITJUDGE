# BITJUDGE by rrishabk

BITJUDGE is a monorepo with a Next.js frontend and a FastAPI backend.

## Stack
- Frontend: Next.js 14, React, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, PostgreSQL, Redis
- Auth: JWT
- Judge: Judge0

## Repository Layout
- `frontend/`: Next.js app
- `backend/`: FastAPI API
- `database/`: SQL schema and seed files
- `infra/`: local Docker Compose setup

## Vercel Deployment Model
Deploy this repo as **two separate Vercel projects**:

1. `bitjudge-backend`
   Root Directory: `backend`
2. `bitjudge-frontend`
   Root Directory: `frontend`

This is the correct setup for this codebase. The frontend runs on Vercel as a Next.js app, and the backend runs on Vercel as Python serverless functions.

## Important Constraint
Vercel can host your frontend and FastAPI backend, but it does **not** replace your infrastructure services.
You still need:

- PostgreSQL: Neon, Supabase, Railway Postgres, Render Postgres, or Vercel Postgres
- Redis: Upstash Redis or another hosted Redis
- Judge0: deploy separately on Railway, Render, VPS, EC2, etc.

Judge0 is not a good fit for Vercel serverless.

## Changes Added For Vercel
- Added `backend/api/index.py` so Vercel can expose the FastAPI app.
- Added `backend/vercel.json` to route all backend requests to the FastAPI entrypoint.
- Disabled the background scheduler automatically on Vercel serverless.
- Made Redis optional so the backend can still boot when Redis is not configured.
- Switched the frontend practice page to use `/api/v1` by default.
- Added a frontend rewrite so `/api/*` can proxy to your deployed backend.
- Added `frontend/.env.example` and updated `backend/.env.example`.

## Local Development
### Frontend
Create `frontend/.env.local`:

```env
BACKEND_URL=http://localhost:8000
```

Then run the frontend from `frontend/`.

### Backend
Create `backend/.env` from `backend/.env.example` and set your local values.

## Step-by-Step: Deploy Backend On Vercel
### 1. Prepare external services
Create these first:
- PostgreSQL database
- Redis instance
- Judge0 instance

Keep the connection strings ready.

### 2. Import the repo into Vercel
In Vercel:
- Click `Add New -> Project`
- Import this Git repository
- Project name: `bitjudge-backend`
- Set `Root Directory` to `backend`

### 3. Backend build settings
Vercel should detect Python automatically because `backend/api/index.py` exists.
You usually do not need a custom build command.

### 4. Add backend environment variables
Set these in the backend Vercel project:

```env
APP_NAME=BITJUDGE
ENVIRONMENT=production
SECRET_KEY=your-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DBNAME
REDIS_URL=redis://default:PASSWORD@HOST:PORT
REDIS_MAX_CONNECTIONS=200
RATE_LIMIT_REQUESTS=120
RATE_LIMIT_WINDOW_SECONDS=60
JUDGE0_URL=https://your-judge0-service.example.com
JUDGE0_API_KEY=
ENABLE_CODEFORCES_SCHEDULER=false
CORS_ORIGINS=["https://your-frontend-domain.vercel.app"]
```

Notes:
- If you do not want Redis immediately, you can leave `REDIS_URL` empty. Rate limiting and cache become no-op.
- On Vercel, the scheduler is already skipped automatically. Keeping `ENABLE_CODEFORCES_SCHEDULER=false` is still the safest production setting.

### 5. Deploy the backend
Deploy the project.
After deploy, verify:

```text
https://your-backend-domain.vercel.app/health
```

It should return:

```json
{"status":"ok"}
```

## Step-by-Step: Run Database SQL
Vercel does not run your SQL migrations automatically.
Run the SQL files on your hosted Postgres manually in this order:

1. `database/migrations/001_init_schema.sql`
2. `database/migrations/002_practice_problem_schema.sql`
3. `database/migrations/003_user_stats.sql`
4. `database/migrations/004_default_admin_email.sql`
5. `database/seed/001_practice_problems.sql`
6. `database/seed/002_default_admin.sql`

Use your Postgres provider SQL editor or `psql`.

## Step-by-Step: Deploy Frontend On Vercel
### 1. Create the frontend project
In Vercel:
- Click `Add New -> Project`
- Import the same Git repository again
- Project name: `bitjudge-frontend`
- Set `Root Directory` to `frontend`

### 2. Add frontend environment variables
Set this in the frontend Vercel project:

```env
BACKEND_URL=https://your-backend-domain.vercel.app
```

Do not add a trailing slash.

What this does:
- Browser requests go to `/api/...` on the frontend domain.
- Next.js rewrites those requests to your backend Vercel URL.
- This avoids browser-side CORS problems for normal app traffic.

### 3. Redeploy frontend after backend URL is known
If you deploy frontend before the backend URL exists, add `BACKEND_URL` later and redeploy.

## Recommended Deployment Order
1. Deploy backend project.
2. Run database migrations and seed data.
3. Confirm backend `/health` works.
4. Add backend URL to frontend `BACKEND_URL`.
5. Deploy frontend project.
6. Test login, practice page, dashboard, and admin flows.

## Required Vercel Root Directories
- Backend project root: `backend`
- Frontend project root: `frontend`

Do not deploy the whole repo as one single Vercel project for this structure.

## Environment Variable Summary
### Backend
```env
APP_NAME=BITJUDGE
ENVIRONMENT=production
SECRET_KEY=your-secret
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DBNAME
REDIS_URL=redis://default:PASSWORD@HOST:PORT
REDIS_MAX_CONNECTIONS=200
RATE_LIMIT_REQUESTS=120
RATE_LIMIT_WINDOW_SECONDS=60
JUDGE0_URL=https://your-judge0-service.example.com
JUDGE0_API_KEY=
ENABLE_CODEFORCES_SCHEDULER=false
CORS_ORIGINS=["https://your-frontend-domain.vercel.app"]
```

### Frontend
```env
BACKEND_URL=https://your-backend-domain.vercel.app
```

## Files Relevant To Deployment
- `backend/api/index.py`
- `backend/vercel.json`
- `backend/.env.example`
- `backend/app/main.py`
- `backend/app/db/session.py`
- `backend/app/core/config.py`
- `frontend/next.config.js`
- `frontend/.env.example`
- `frontend/app/practice/page.tsx`

## What To Test After Deploy
- Frontend loads on the Vercel domain
- Backend `/health` returns 200
- Login works
- Protected routes redirect correctly
- Practice API requests reach the backend through `/api/v1/...`
- Backend can connect to Postgres
- Backend can connect to Redis if configured
- Judge0 submission flow works against your external Judge0 service
