# Privacy

## Scope

This document describes how the application handles uploaded media,
live camera frames, stored metadata, and logs.

Operators deploying the application are responsible for complying with
applicable privacy, consent, retention, and deletion requirements.

## Image and video uploads

Uploaded image and video files are stored locally in the configured
application upload volume.

Generated annotated images and videos are stored in the configured
result volume.

Uploaded and generated files remain stored until they are deleted by
the operator or by an implemented retention process.

Operators are responsible for:

- Obtaining appropriate permission to process uploaded media
- Defining retention periods
- Deleting expired or unnecessary files
- Restricting access to stored media
- Protecting backups containing uploaded or generated files

Uploaded files and generated results must not be committed to Git.

## Live camera

The browser requests camera video permission.

Audio permission is not requested, and audio is not captured by the
application.

Camera frames are:

1. Captured by the browser.
2. Encoded as temporary JPEG frames.
3. Sent to FastAPI through a WebSocket connection.
4. Processed temporarily for object detection and tracking.
5. Discarded after the frame result is produced.

The application does not store camera frames as source images or video
recordings.

The application may store the following camera-session information:

- Session metadata
- Session start and completion times
- Processed frame counts
- Detection counts
- Unique track counts
- Representative track records
- Object classes
- Confidence values
- Bounding-box coordinates

These records do not include the original camera frame.

## Database data

MySQL stores application metadata, including:

- Detection job identifiers
- Job status and progress
- Source type
- Processing duration
- Detection counts
- Object classes
- Confidence values
- Bounding-box coordinates
- Representative tracking identifiers

Database access must be restricted to authorized application services
and operators.

## Logging

Application logs may contain operational information such as:

- Request identifiers
- HTTP methods
- Request paths
- Response status codes
- Processing duration
- Job identifiers
- Error details

Logs must not contain:

- Raw image or video content
- Camera frames
- Complete multipart request bodies
- Database passwords
- Redis passwords
- Authentication tokens
- Secret environment variables
- Full connection strings containing credentials
- Model files
- Private encryption keys

File names and paths should also be treated carefully because they may
contain user-provided or identifying information.

## Backups

Database and media backups may contain the same sensitive information
as the live application storage.

Backups must be:

- Stored securely
- Accessible only to authorized operators
- Protected from accidental publication
- Included in retention and deletion policies
- Tested for recovery
- Excluded from Git

## Remote deployment

Remote deployments should use:

- HTTPS for HTTP and WebSocket traffic
- Access controls
- Secure secret management
- Restricted database and Redis network access
- Protected persistent volumes
- Secure backup storage
- Defined retention and deletion procedures
- Monitoring that does not expose sensitive media or credentials

The local production demonstration configuration should not be exposed
directly to the public internet without additional security controls.