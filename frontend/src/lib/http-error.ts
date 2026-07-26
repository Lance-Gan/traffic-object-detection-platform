import axios from "axios";

interface ApiErrorBody {
  detail?: unknown;
}

export function getErrorMessage(error: unknown): string {
  if (!axios.isAxiosError<ApiErrorBody>(error)) {
    return "An unexpected error occurred";
  }

  if (error.code === "ECONNABORTED") {
    return "The detection request timed out";
  }

  if (!error.response) {
    return "The API server could not be reached";
  }

  const detail = error.response.data?.detail;

  if (typeof detail === "string" && detail.trim().length > 0) {
    return detail;
  }

  switch (error.response.status) {
    case 400:
      return "The selected file is not a valid image";

    case 413:
      return "The selected image exceeds the upload limit";

    case 415:
      return "Only JPEG, PNG, and WebP images are supported";

    case 500:
      return "The server could not complete image detection";

    default:
      return `The request failed with status ${error.response.status}`;
  }
}
