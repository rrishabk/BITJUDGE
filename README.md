# BITJUDGE

Production-oriented monorepo scaffold for a coding platform powered by BITWISE.

## Stack
- Frontend: Next.js 14, React, TailwindCSS, Shadcn-style UI primitives, Recharts
- Backend: FastAPI, PostgreSQL, Redis, Judge0
- Auth: JWT with `@juetguna.in` email restriction

## Services
- `frontend/`: app router frontend with student, quiz, practice, and admin dashboards
- `backend/`: async FastAPI API with JWT auth, quiz management, practice tracking, and Judge0 submission flow
- `database/seed/`: starter practice-problem dataset for CSES and Codeforces 800-1600
- `infra/`: Docker Compose and Nginx reverse proxy

## Local Run
1. Copy `backend/.env.example` to `backend/.env` and change secrets.
2. Install frontend dependencies in `frontend/` and backend dependencies in `backend/`.
3. Start infrastructure with `docker compose -f infra/docker-compose.yml up --build`.
4. Open `http://localhost`.

## Notes
- The frontend currently uses mock dashboard data for visual scaffolding.
- The backend models and endpoints are ready to be connected to real frontend API calls.
- Replace the placeholder migration process with Alembic revisions before deployment.
# Stack

- `frontend`: Next.js app for authentication, problem browsing, code submission, and result views
- `backend`: FastAPI service for auth, problem APIs, submissions, and judge orchestration
- `database`: PostgreSQL for users, problems, contests, submissions, and verdict history
- `redis`: short-lived session cache, rate limiting, queue metadata, and hot leaderboard data
- `judge-service`: Judge0 API for code execution and verdict generation

## Suggested Repository Layout

```text
BITJUDGE/
├── frontend/                 # Next.js
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   └── package.json
├── backend/                  # FastAPI
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── database/
│   ├── migrations/
│   └── seed/
├── infra/
│   ├── docker-compose.yml
│   ├── nginx/
│   └── env/
└── read.md
```

## Service Responsibilities

### Frontend

- Handles login, registration, and protected routes
- Shows problems, editor UI, submission history, and contest pages
- Calls FastAPI over REST or WebSocket for live verdict updates

### Backend

- Validates users and issues auth tokens or session identifiers
- Stores and fetches problems, test cases, and submissions
- Sends source code to Judge0 and polls or receives callback results
- Updates PostgreSQL with verdicts, runtime, memory, and logs
- Uses Redis for session caching, throttling, and background job state

### PostgreSQL

Main tables:

- `users`
- `problems`
- `problem_testcases`
- `submissions`
- `submission_results`
- `contests`
- `contest_registrations`
- `leaderboards`

### Redis

Typical uses:

- session store
- refresh token blacklist
- submission queue state
- rate limiting counters
- cached leaderboard snapshots

### Judge0

- Receives source code, language id, stdin, expected output, and limits
- Returns compile status, execution status, time, memory, stdout, stderr

## Submission Flow

1. User writes code in the Next.js frontend.
2. Frontend sends submission payload to FastAPI.
3. FastAPI stores a `pending` submission row in PostgreSQL.
4. FastAPI pushes temporary submission state into Redis.
5. FastAPI sends the job to Judge0.
6. Judge0 executes code and returns a token/result.
7. FastAPI resolves the result, updates PostgreSQL, and invalidates Redis state.
8. Frontend fetches or subscribes to the final verdict.

## Recommended API Surface

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

### Problems

- `GET /problems`
- `GET /problems/{problem_id}`
- `POST /problems` for admin

### Submissions

- `POST /submissions`
- `GET /submissions/{submission_id}`
- `GET /submissions/user/{user_id}`

### Contests

- `GET /contests`
- `GET /contests/{contest_id}`
- `GET /contests/{contest_id}/leaderboard`

## Core Environment Variables

```env
# frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# backend
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/bitjudge
REDIS_URL=redis://redis:6379/0
JUDGE0_URL=http://judge0:2358
JUDGE0_API_KEY=
SECRET_KEY=
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Initial Build Order

1. Create `docker-compose.yml` for PostgreSQL, Redis, backend, and frontend.
2. Build FastAPI auth and problem APIs first.
3. Add PostgreSQL models and Alembic migrations.
4. Integrate Judge0 submission pipeline.
5. Build Next.js pages for auth, problems, and submissions.
6. Add leaderboard caching and contest features.

## MVP Features

- User authentication
- Problem listing and detail page
- Code editor with language selection
- Run/submit code
- Verdict, runtime, and memory display
- Submission history
- Basic admin problem management

## Future Extensions

- contest timers and rank freezing
- plagiarism detection
- discussion threads
- code templates by language
- rejudge support
- websocket-based live verdict streaming
