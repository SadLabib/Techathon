// Base URL of the FastAPI backend. Override with VITE_API_BASE if needed.
export const API_BASE =
  import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

// http://host -> ws://host, https://host -> wss://host
export const WS_URL = API_BASE.replace(/^http/, "ws") + "/ws";
