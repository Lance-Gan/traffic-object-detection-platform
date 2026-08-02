class ApplicationError(Exception):
    """Base class for application-level errors."""


class UnsupportedImageTypeError(ApplicationError):
    """Raised when the uploaded media type is not supported."""


class ImageTooLargeError(ApplicationError):
    """Raised when an uploaded image exceeds the configured limit."""


class InvalidImageError(ApplicationError):
    """Raised when uploaded content is not a valid image."""


class EmptyFileError(ApplicationError):
    """Raised when an uploaded file contains no data."""


class DetectionProcessingError(ApplicationError):
    """Raised when object detection cannot be completed."""


class UnsupportedVideoTypeError(ApplicationError):
    """Raised when the uploaded video type is unsupported."""


class VideoTooLargeError(ApplicationError):
    """Raised when an uploaded video exceeds the size limit."""


class InvalidVideoError(ApplicationError):
    """Raised when uploaded content is not a valid video."""


class VideoTooLongError(ApplicationError):
    """Raised when an uploaded video exceeds the duration limit."""


class InvalidCameraFrameError(ApplicationError):
    """Raised when a camera frame cannot be decoded safely."""


class CameraSessionUnavailableError(ApplicationError):
    """Raised when a camera session cannot be opened."""
