# Contributing

Thank you for your interest in contributing to the Real-Time Traffic Object
Detection Platform.

This repository is primarily a portfolio and learning project. Contributions
should remain focused, testable, and consistent with the existing architecture.

## Development workflow

1. Create a feature branch from the latest main branch.
2. Make focused changes.
3. Add or update tests when behaviour changes.
4. Run the relevant quality checks.
5. Update documentation when required.
6. Open a pull request.
7. Wait for continuous integration checks to pass.

Avoid combining unrelated backend, frontend, infrastructure, and documentation
changes in the same pull request.

## Branch naming

Use a short category prefix followed by a descriptive name.

Examples:

```text
feature/video-retention
fix/camera-cleanup
docs/deployment-guide
test/websocket-errors
refactor/detection-service
chore/dependency-update
```

Recommended prefixes:

| Prefix | Purpose |
| --- | --- |
| `feature/` | New user-facing functionality |
| `fix/` | Bug fixes |
| `docs/` | Documentation changes |
| `test/` | Test additions or corrections |
| `refactor/` | Internal code restructuring |
| `chore/` | Maintenance and dependency work |

## Backend setup

From the project root:

```bash
cd backend

source .venv/bin/activate

python -m pip install \
  --requirement requirements.txt

python -m pip install \
  --requirement requirements-dev.txt
```

Start the local MySQL and Redis services when required:

```bash
cd ..

docker compose up \
  --detach \
  mysql \
  redis
```

## Backend quality checks

From the `backend` directory:

```bash
python -m pip check

ruff format --check \
  app \
  tests \
  scripts

ruff check \
  app \
  tests \
  scripts

mypy \
  app \
  scripts

alembic check

python -m pip_audit
```

Run backend integration tests through the isolated test script:

```bash
./scripts/test_backend.sh
```

Do not run `pytest` directly unless the isolated test MySQL and Redis services
are already running.

The backend test script:

1. Starts the test MySQL and Redis containers.
2. Applies Alembic migrations.
3. Runs pytest and coverage.
4. Stops the test containers.

## Frontend setup

From the project root:

```bash
cd frontend

npm ci
```

## Frontend quality checks

```bash
npm run format:check
npm run lint
npm run typecheck
npm run test:coverage
npm run build
```

Run browser tests when changes affect routing, page rendering, uploads, or user
workflows:

```bash
npm run test:e2e
```

Check dependencies:

```bash
npm audit \
  --audit-level=high
```

Do not use `npm audit fix --force` without reviewing the resulting dependency
changes.

## Docker checks

Validate the Compose files:

```bash
docker compose config

docker compose \
  --env-file .env.production \
  --file compose.production.yml \
  config
```

Build the affected production images when changing Dockerfiles, dependencies,
Nginx configuration, or Compose configuration:

```bash
docker compose \
  --env-file .env.production \
  --file compose.production.yml \
  build
```

Do not commit:

- `.env.production`
- model weights
- uploaded media
- generated result media
- database exports
- backup archives
- browser recordings containing private information

## Commit messages

Use clear and focused commit messages.

Examples:

```text
feat: add result retention settings
fix: close camera session after disconnect
test: cover video task failure
docs: explain CPU Docker deployment
refactor: separate camera tracking state
chore: update backend dependencies
```

Recommended prefixes include:

```text
feat
fix
docs
test
refactor
chore
ci
build
```

A commit should represent one understandable change.

## Pull requests

A pull request should explain:

- What changed
- Why it changed
- How it was tested
- Any database migration impact
- Any deployment or configuration impact
- Any security or privacy implications
- Any known limitations

Include screenshots when changing visible frontend behaviour.

Do not include passwords, tokens, private media, production database exports, or
camera frames in a pull request.

## Database migrations

Create an Alembic migration when changing the database schema.

Review generated migrations before committing them.

Run:

```bash
cd backend

source .venv/bin/activate

alembic upgrade head
alembic check
```

A pull request containing a migration should explain:

- What schema changed
- Whether existing data is affected
- Whether deployment order matters
- Whether rollback has limitations

## Documentation

Update the relevant documentation when behaviour changes:

```text
README.md
docs/ARCHITECTURE.md
docs/DEPLOYMENT.md
docs/PRIVACY.md
docs/testing.md
SECURITY.md
CHANGELOG.md
```

Keep documentation aligned with the actual repository and implemented
behaviour.

## Security reports

Do not report sensitive vulnerabilities through a public issue.

Follow the private reporting guidance in:

```text
SECURITY.md
```

## Before submitting

From the project root, check the final changes:

```bash
git status --short
git diff --check
```

Confirm that no secrets, private media, model weights, generated files, or
unrelated changes are included.
