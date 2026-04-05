import { useCallback, useState } from "react";

import { apiGet, apiPost } from "../services/api";
import type { RuleApproveResponse, RuleListResponse } from "../types/rule";

type ApprovePayload = {
  blindSpotId?: string;
  action?: "approve" | "modify" | "dismiss";
  cypher?: string;
  timestamp?: string;
};

export function useRules() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const list = useCallback(async (): Promise<RuleListResponse> => {
    return apiGet<RuleListResponse>("/rules");
  }, []);

  const approve = useCallback(async (payload: ApprovePayload): Promise<RuleApproveResponse> => {
    setLoading(true);
    setError(null);
    try {
      return await apiPost<RuleApproveResponse>("/rules/approve", payload);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Rule approval failed";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { list, approve, loading, error };
}
