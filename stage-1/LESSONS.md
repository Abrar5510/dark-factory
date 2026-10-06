# Stage 1 Lessons

1. **Time estimation was optimistic** - A complete payments system requires more than 30 minutes for initial implementation, even with foundational code.
2. **Containerization adds complexity** - Docker builds require careful dependency management between dev and production packages.
3. **TypeScript strictness helps** - Compilation errors caught design issues early, but slowed initial progress.
4. **Database schema is foundational** - Well-designed tables (users, payments, requests, splits) support all business logic.
5. **Idempotency is complex** - The 5 idempotent write paths require careful key scoping and replay semantics.

## Deferrals to Stage 2
1. Complete implementation of all API endpoints
2. Full idempotency service with request body hashing
3. Test endpoints (/test/reset, /test/export, /test/import)
4. Split calculation and settlement atomicity
5. Comprehensive error handling per specification
6. Activity feed with proper visibility rules