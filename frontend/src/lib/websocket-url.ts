import { env } from "./env";

export function resolveWebSocketUrl(path: string): string {
  const apiUrl = new URL(env.VITE_API_BASE_URL, window.location.origin);

  apiUrl.protocol = apiUrl.protocol === "https:" ? "wss:" : "ws:";

  return new URL(path, apiUrl).toString();
}
