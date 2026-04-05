import { useCallback, useState } from "react";

import { apiPost } from "../services/api";
import type { RedTeamRunRequest, RedTeamRunResponse } from "../types/attack";

export function useRedTeam() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(async (payload: RedTeamRunRequest): Promise<RedTeamRunResponse> => {
    setLoading(true);
    setError(null);
    try {
      return await apiPost<RedTeamRunResponse>("/redteam/run", payload);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Red Team run failed";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { run, loading, error };
}
