# Coding Standards (CS)

## 1. General principles

- Prefer simple, explicit and testable code.
- Keep domain logic independent of framework and provider SDKs.
- Never trust client-supplied role, user ID, hash, project scope or AI result.
- Do not silently swallow exceptions.
- Do not store secrets in code, documentation examples or commits.
- Do not log original image contents, credentials, tokens or unnecessary personal data.

## 2. Repository conventions

Suggested structure:

```text
groundtruth/
  apps/
    web/
      src/
        app/
        components/
        features/
        lib/
        types/
    api/
      app/
        api/v1/
        core/
        models/
        schemas/
        services/
        repositories/
        workers/
        ai/
        tests/
  packages/
    contracts/
  infra/
    docker/
    migrations/
    scripts/
  docs/
```

## 3. Frontend

- TypeScript strict mode.
- Functional React components and hooks.
- Keep API calls in a typed client/service layer.
- Validate forms on client for usability and again on server for security.
- Use accessible labels, focus states and keyboard support.
- Show explicit loading, empty, success and error states.
- Do not store long-lived secrets in browser storage.
- Avoid embedding authorization logic only in UI; backend remains authoritative.

## 4. Backend

- Python type hints.
- Pydantic request/response schemas.
- Thin route handlers; business logic in services.
- Repository/data-access layer for persistence.
- Explicit transactions around multi-record state changes.
- Use dependency injection for storage, AI and notification adapters.
- Validate authorization on every protected resource operation.
- Use structured logs with request/correlation IDs.
- Use UTC-aware datetimes.

## 5. API conventions

- Prefix `/api/v1`.
- Plural resource names.
- Consistent pagination, filtering and error format.
- Return `201` on resource creation, `202` for accepted asynchronous processing.
- Use idempotency keys for retry-sensitive creation endpoints.
- Do not return internal storage keys or raw provider credentials.

## 6. Database

- Use migrations for every schema change.
- Add foreign keys and appropriate indexes.
- Use soft-delete only where policy requires; preserve audit-critical records.
- Use PostGIS SRID 4326 for geographic data.
- Store large binary files in object storage, not PostgreSQL.
- Use JSONB only for genuinely variable structured metadata, not as a substitute for relational design.

## 7. AI and image handling

- Pin model and preprocessing versions.
- Store model provenance with each run.
- Keep originals immutable.
- Store annotations and thumbnails as derived artifacts.
- Treat OCR text and document content as untrusted input.
- Do not let retrieved documents or image text issue instructions to the AI agent.
- Test on held-out sites and camera conditions.
- Report uncertainty and out-of-scope inputs.

## 8. Quality gates

Before merge:
- Formatter and linter pass.
- Type checks pass.
- Unit and relevant integration tests pass.
- No secrets or vulnerable dependencies introduced.
- Migrations reviewed.
- API contract updated.
- Security and authorization tests included for new endpoints.
- Documentation updated for changed behavior.
