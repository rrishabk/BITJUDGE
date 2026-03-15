BEGIN;

ALTER TABLE practice_problems
    ADD COLUMN IF NOT EXISTS tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS contest_id INTEGER,
    ADD COLUMN IF NOT EXISTS problem_index VARCHAR(16);

CREATE INDEX IF NOT EXISTS idx_practice_problems_contest_id ON practice_problems(contest_id);

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'problem_progress'
    ) AND NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'user_problem_progress'
    ) THEN
        ALTER TABLE problem_progress RENAME TO user_problem_progress;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS user_problem_progress (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    problem_id BIGINT NOT NULL REFERENCES practice_problems(id) ON DELETE CASCADE,
    solved BOOLEAN NOT NULL DEFAULT FALSE,
    solved_at TIMESTAMPTZ,
    CONSTRAINT user_problem_progress_unique UNIQUE (user_id, problem_id)
);

ALTER TABLE user_problem_progress
    ADD COLUMN IF NOT EXISTS solved_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_user_problem_progress_user_id ON user_problem_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_problem_progress_problem_id ON user_problem_progress(problem_id);

COMMIT;
