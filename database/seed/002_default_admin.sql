CREATE EXTENSION IF NOT EXISTS pgcrypto;

INSERT INTO users (
    name,
    enrollment_number,
    email,
    password_hash,
    role,
    created_at
)
VALUES (
    'BITJUDGE Admin',
    'ADMIN001',
    'admin@juetguna.in',
    crypt('admin@8279ViJio', gen_salt('bf')),
    'admin',
    NOW()
)
ON CONFLICT (email) DO NOTHING;

INSERT INTO user_stats (user_id, problems_solved, total_score, streak_days, last_submission)
SELECT u.id, 0, 0, 0, NULL
FROM users u
WHERE u.email = 'admin@juetguna.in'
ON CONFLICT (user_id) DO NOTHING;
