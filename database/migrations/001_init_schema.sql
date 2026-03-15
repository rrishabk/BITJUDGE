BEGIN;

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    enrollment_number VARCHAR(32) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'admin')),
    codeforces_handle VARCHAR(64),
    codechef_handle VARCHAR(64),
    leetcode_handle VARCHAR(64),
    hackerrank_handle VARCHAR(64),
    github_handle VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT users_email_domain_check CHECK (email ~* '^[A-Z0-9._%+-]+@juetguna\.in$')
);

CREATE TABLE IF NOT EXISTS quizzes (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    created_by BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT quizzes_time_check CHECK (end_time > start_time)
);

CREATE TABLE IF NOT EXISTS quiz_questions (
    id BIGSERIAL PRIMARY KEY,
    quiz_id BIGINT NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    question_type VARCHAR(10) NOT NULL CHECK (question_type IN ('mcq', 'coding')),
    question_text TEXT NOT NULL,
    topic VARCHAR(120) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_quiz_questions_quiz_id ON quiz_questions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_quiz_questions_type ON quiz_questions(question_type);
CREATE INDEX IF NOT EXISTS idx_quiz_questions_topic ON quiz_questions(topic);

CREATE TABLE IF NOT EXISTS mcq_options (
    id BIGSERIAL PRIMARY KEY,
    question_id BIGINT NOT NULL REFERENCES quiz_questions(id) ON DELETE CASCADE,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_mcq_options_question_id ON mcq_options(question_id);

CREATE TABLE IF NOT EXISTS coding_questions (
    id BIGSERIAL PRIMARY KEY,
    question_id BIGINT NOT NULL UNIQUE REFERENCES quiz_questions(id) ON DELETE CASCADE,
    input_format TEXT NOT NULL,
    output_format TEXT NOT NULL,
    sample_input TEXT,
    sample_output TEXT
);

CREATE TABLE IF NOT EXISTS submissions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id BIGINT NOT NULL REFERENCES quiz_questions(id) ON DELETE CASCADE,
    code TEXT NOT NULL,
    language VARCHAR(20) NOT NULL CHECK (language IN ('C++', 'C', 'Java', 'Python')),
    verdict VARCHAR(50) NOT NULL DEFAULT 'pending',
    score NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (score >= 0 AND score <= 100),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_submissions_user_id ON submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_submissions_question_id ON submissions(question_id);
CREATE INDEX IF NOT EXISTS idx_submissions_submitted_at ON submissions(submitted_at DESC);

CREATE TABLE IF NOT EXISTS practice_problems (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    link TEXT NOT NULL UNIQUE,
    difficulty INTEGER NOT NULL CHECK (difficulty >= 0),
    topic VARCHAR(120) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_practice_problems_platform ON practice_problems(platform);
CREATE INDEX IF NOT EXISTS idx_practice_problems_difficulty ON practice_problems(difficulty);
CREATE INDEX IF NOT EXISTS idx_practice_problems_topic ON practice_problems(topic);

CREATE TABLE IF NOT EXISTS user_problem_progress (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    problem_id BIGINT NOT NULL REFERENCES practice_problems(id) ON DELETE CASCADE,
    solved BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT user_problem_progress_unique UNIQUE (user_id, problem_id)
);

CREATE INDEX IF NOT EXISTS idx_user_problem_progress_user_id ON user_problem_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_problem_progress_problem_id ON user_problem_progress(problem_id);

COMMIT;
