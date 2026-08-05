# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog principles, and the project uses
semantic versioning where practical.

## [Unreleased]

### Added

- Project screenshots and demonstration media.
- Expanded deployment, architecture, privacy, security, and contribution
  documentation.

### Changed

- Production Docker images use CPU-only PyTorch on macOS and other non-NVIDIA
  environments.
- Server-side computer-vision dependencies use headless OpenCV.
- Backend integration tests run through isolated MySQL and Redis test services.

### Fixed

- Added the tracking dependency required by Ultralytics video tracking.
- Corrected production dependency validation for CPU-only containers.

## [1.0.0] - 2026-08-06

### Added

- Image object detection for JPEG, PNG, and WebP uploads.
- Annotated image-result generation.
- Asynchronous video processing with Redis and Celery.
- Persistent video tracking with YOLO and ByteTrack.
- Total-detection and unique-track counting semantics.
- FFmpeg H.264 video-result encoding.
- Browser-camera detection through WebSocket communication.
- Browser-side bounding-box rendering with HTML canvas.
- Camera-session metrics and representative-track persistence.
- Detection history with pagination, search, and filters.
- Analytics dashboards with job, source, class, and daily activity statistics.
- MySQL persistence with SQLAlchemy 2.
- Database migrations with Alembic.
- FastAPI REST and WebSocket APIs.
- React and TypeScript frontend.
- TanStack Query server-state management.
- ECharts analytics visualisations.
- Structured JSON logging.
- Request identifiers for log correlation.
- Upload-size and decoded-content validation.
- Trusted-host, CORS, WebSocket-origin, and security-header controls.
- Non-root application containers.
- Isolated Docker networks.
- Read-only model mounts.
- Nginx static hosting, API proxying, WebSocket proxying, and media delivery.
- Docker Compose development, testing, and production-demonstration
  configurations.
- MySQL and media backup tooling.
- Backend unit and API integration tests.
- Camera WebSocket protocol tests.
- Frontend component and utility tests.
- Playwright browser smoke tests.
- Ruff formatting and linting.
- Mypy static type checking.
- ESLint, TypeScript, and Prettier checks.
- Python and JavaScript dependency vulnerability scanning.
- GitHub Actions continuous integration.
- Dependabot dependency update configuration.
- Architecture documentation.
- Deployment documentation.
- Privacy and retention documentation.
- Security reporting policy.
- Contribution guidelines.
- Project README with setup, API, testing, and operational instructions.

### Security

- Added UUID-based stored filenames.
- Added bounded upload and request-body limits.
- Added camera-frame byte and decoded-pixel limits.
- Added safe public error responses.
- Added non-root container execution.
- Added restricted service networking.
- Added guidance against public exposure of the local demonstration stack.

### Known limitations

- Authentication and user accounts are not included.
- Role-based authorisation and multi-tenant isolation are not included.
- Docker inference on macOS uses CPU rather than Apple MPS.
- Apple MPS acceleration requires native macOS execution.
- The production Compose configuration targets a single-host demonstration.
- Model weights are not included in the repository.
- Generated-media retention and deletion remain operator responsibilities.
