import { useEffect, useMemo, useState } from "react";

import { apiGet } from "../services/api";

type EventsHealth = {
  events: string;
};

export function useSSE(enabled = true) {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastEvent, setLastEvent] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled) {
      setConnected(false);
      return;
    }

    let cancelled = false;

    async function checkEventsHealth() {
      try {
        const data = await apiGet<EventsHealth>("/events");
        if (cancelled) {
          return;
        }
        setConnected(true);
        setLastEvent(data.events);
        setError(null);
      } catch (err) {
        if (cancelled) {
          return;
        }
        setConnected(false);
        setError(err instanceof Error ? err.message : "Events endpoint unavailable");
      }
    }

    void checkEventsHealth();
    const interval = window.setInterval(() => {
      void checkEventsHealth();
    }, 15000);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [enabled]);

  const status = useMemo(() => {
    if (!enabled) {
      return "disabled";
    }
    return connected ? "connected" : "disconnected";
  }, [connected, enabled]);

  return { connected, status, error, lastEvent };
}
