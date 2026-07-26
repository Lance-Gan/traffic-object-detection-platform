import axios from "axios";

import { env } from "../lib/env";

export const apiClient = axios.create({
  baseURL: env.VITE_API_BASE_URL,
  timeout: 120_000,
  withCredentials: false,
  headers: {
    Accept: "application/json",
  },
});
