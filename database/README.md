# Database

SkillForge uses:

- **PostgreSQL** for structured data (users, projects, submissions, courses, jobs, challenges)
- **MongoDB** for analytics and activity logs

In dev, tables are created automatically on backend startup via SQLAlchemy `Base.metadata.create_all`.

For production, add Alembic migrations in `backend/alembic/` (already dependency-installed).

