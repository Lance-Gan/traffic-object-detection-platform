# Testing Strategy

## Coverage Baseline

Baseline recorded on 2026-08-03.

### Backend

| Metric | Baseline |
| --- | ---: |
| Total coverage | 56.00% |

Run:

```bash
cd backend
./scripts/test_backend.sh
```

Backend tests use an isolated MySQL test database and fake inference services.

### Frontend

| Metric | Baseline |
| --- | ---: |
| Statements | 2.12% |
| Branches | 3.37% |
| Functions | 3.01% |
| Lines | 2.15% |

Run unit tests with coverage:

```bash
cd frontend
npm run test:coverage
```

Run browser end-to-end tests:

```bash
npm run test:e2e
```

## Coverage Policy

Coverage must not decrease without an explanation in the pull request.

Priority areas:

- Upload validation
- Job status transitions
- Database persistence
- WebSocket control messages
- Error handling
- Polling termination
- Statistics calculations

Coverage thresholds should be introduced gradually from the recorded baseline. Critical business files must not be excluded solely to make CI pass.
