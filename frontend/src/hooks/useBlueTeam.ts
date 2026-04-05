import { useCallback, useState } from "react";

import { apiGet, apiPost } from "../services/api";
import type { ForensicTimelineResponse } from "../types/audit";
import type { Detection } from "../types/detection";

type EvaluatePayload = {
  attack_id: string;
  content: string;
  source?: string;
  metadata?: Record<string, string>;
};

export function useBlueTeam() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const evaluate = useCallback(async (payload: EvaluatePayload): Promise<Detection> => {
    setLoading(true);
    setError(null);
    try {
      return await apiPost<Detection>("/blueteam/evaluate", payload);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Blue Team evaluation failed";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getForensics = useCallback(async (attackId: string): Promise<ForensicTimelineResponse> => {
    return apiGet<ForensicTimelineResponse>(`/blueteam/forensics/${attackId}`);
  }, []);

  return { evaluate, getForensics, loading, error };
}
