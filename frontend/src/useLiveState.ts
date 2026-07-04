import { useEffect, useRef, useState } from "react";
import type { Snapshot } from "./types";
import { API_BASE, WS_URL } from "./api";

/**
 * Subscribes to live office state:
 *  1. fetches an initial snapshot over REST (so the UI paints instantly), then
 *  2. opens a WebSocket for live pushes, auto-reconnecting if it drops.
 */
export function useLiveState() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let closed = false;

    fetch(`${API_BASE}/api/devices`)
      .then((r) => r.json())
      .then((data: Snapshot) => setSnapshot((prev) => prev ?? data))
      .catch(() => {});

    function connect() {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);
      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          if (msg.type === "snapshot") setSnapshot(msg.data as Snapshot);
        } catch {
          /* ignore malformed frames */
        }
      };
      ws.onclose = () => {
        setConnected(false);
        if (!closed) setTimeout(connect, 1500); // auto-reconnect
      };
      ws.onerror = () => ws.close();
    }

    connect();

    return () => {
      closed = true;
      wsRef.current?.close();
    };
  }, []);

  return { snapshot, connected };
}
