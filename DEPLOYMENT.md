# Deployment and Operations

## 1. Environments

- Local development: Docker Compose, seeded demo data.
- Test/CI: isolated ephemeral database and object storage.
- Staging: production-like configuration with synthetic or approved test data.
- Production: isolated credentials, private network paths and monitored services.

## 2. Containers

Suggested services:
- `web`
- `api`
- `worker`
- `postgres` with PostGIS
- `redis`
- `object-storage` for local development only
- optional `flower`/queue dashboard restricted to operators

## 3. Configuration

Use environment variables or managed secrets:
- `DATABASE_URL`
- `REDIS_URL`
- `OBJECT_STORAGE_ENDPOINT`
- `OBJECT_STORAGE_BUCKET`
- `OBJECT_STORAGE_ACCESS_KEY`
- `OBJECT_STORAGE_SECRET_KEY`
- `JWT_SECRET` or identity provider settings
- `AI_MODEL_PATH` / provider settings
- `APP_ENV`
- `CORS_ORIGINS`

Never commit real values. Provide `.env.example` with placeholders only.

## 4. CI/CD

1. Install dependencies with lockfiles.
2. Run formatters and linters.
3. Run static type checks.
4. Run unit tests.
5. Run integration tests.
6. Build containers.
7. Scan dependencies and images.
8. Apply migrations in controlled deployment step.
9. Deploy to staging.
10. Run smoke tests.
11. Promote to production with rollback plan.

## 5. Observability

Monitor:
- API latency and error rate.
- Upload success/failure.
- Worker queue depth and job age.
- AI task duration and failure by pipeline stage.
- Database health and connection pool.
- Object storage availability.
- Authentication failures and suspicious access.
- Reviewer queue age.
- Hash verification mismatches.

Use structured logs with correlation IDs. Do not log secrets or raw sensitive evidence.

## 6. Backup and recovery

- Automated PostgreSQL backups.
- Point-in-time recovery if supported.
- Object storage versioning/replication according to risk.
- Periodic restore drills.
- Define RPO and RTO with the project owner.
- Document recovery steps and responsible operators.

## 7. Operational runbooks

Create runbooks for:
- Database outage.
- Object storage outage.
- Queue backlog.
- AI provider/model outage.
- Hash mismatch.
- Suspected unauthorized access.
- Failed migration.
- Backup restoration.
