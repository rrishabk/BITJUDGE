BEGIN;

ALTER TABLE users DROP CONSTRAINT IF EXISTS users_email_domain_check;

ALTER TABLE users
    ADD CONSTRAINT users_email_domain_check
    CHECK (
        email ~* '^[A-Z0-9._%+-]+@juetguna\.in$'
        OR lower(email) = 'admin@juetguna.in'
    );

COMMIT;
