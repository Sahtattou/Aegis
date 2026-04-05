export type Attack = {
  attack_id: string;
  persona: string;
  content: string;
  severity: string;
  techniques: string[];
  novelty_score: number;
  max_similarity: number;
};

export type RedTeamRunRequest = {
  target: string;
  objective: string;
  n_attacks: number;
};

export type RedTeamRunResponse = {
  status: string;
  target: string;
  objective: string;
  n_attacks: number;
  attacks: Attack[];
};
