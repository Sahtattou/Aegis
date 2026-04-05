import { useCallback, useEffect, useState } from "react";

import { apiGet } from "../services/api";
import type { AuditEntry } from "../types/audit";

export function useAudit(limit = 50) {
  const [timeline, setTimeline] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiGet<AuditEntry[]>(`/audit/timeline?limit=${limit}`);
      setTimeline(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load audit timeline");
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { timeline, refresh, loading, error };
}
