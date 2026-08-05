# Deployment

## Local production demonstration

### Requirements

- Docker Desktop
- Docker Compose
- Ultralytics model weight
- At least one supported browser

### Prepare configuration

```bash
cp .env.production.example .env.production
chmod 600 .env.production
```

Set secure production passwords and secrets before starting the stack.

Do not commit `.env.production` to Git.

### Prepare the model

Place the model at:

```text
models/yolo26n.pt
```

Confirm that the model exists:

```bash
ls -lh models/yolo26n.pt
```

Model weights are supplied outside Git and must not be committed to the repository.

### Start

```bash
./scripts/production_up.sh
```

Open:

```text
http://127.0.0.1:8080
```

### Status

```bash
./scripts/production_status.sh
```

### Logs

```bash
docker compose \
  --env-file .env.production \
  --file compose.production.yml \
  logs \
  --follow \
  --tail=200
```

Press `Control + C` to stop following the logs. This does not stop the containers.

### Backup

```bash
./scripts/backup_production.sh
```

Backups are written to:

```text
backups/
```

Verify that database and media backup archives were created successfully.

### Stop

```bash
./scripts/production_down.sh
```

## Important macOS limitation

The complete Docker stack uses CPU inference on macOS.

Docker Desktop runs Linux containers inside a virtual machine and does not
provide Apple MPS acceleration to the containers.

For Apple MPS acceleration, run FastAPI and Celery directly in the macOS
Python environment and keep MySQL and Redis in Docker.

## Remote deployment

A remote deployment requires:

- A Linux server
- HTTPS
- A domain or trusted endpoint
- Persistent storage
- Automated and tested backups
- External secret management
- Monitoring and health checks
- Firewall and network access controls
- A supported GPU runtime when GPU inference is required

The local production demonstration configuration should not be exposed
directly to the public internet without additional security hardening.