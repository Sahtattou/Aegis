export type Rule = {
  id: string;
  pattern: string;
  description?: string;
  decision?: "malicious" | "suspicious" | "benign";
  confidence?: number;
  enabled?: boolean;
};

export type RuleListResponse = {
  count: number;
};

export type RuleApproveResponse = {
  status: string;
};
