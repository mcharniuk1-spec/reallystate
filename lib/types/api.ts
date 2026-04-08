export type DevHealth = {
  status: string;
  service?: string;
  stage?: string;
  note?: string;
};

export type SourceRow = {
  source_name: string;
  tier: number;
  family: string;
  access_mode: string;
  legal_mode: string;
  risk_mode: string;
  mvp_phase: number;
  primary_url: string;
};

export type SourcesPayload = {
  count: number;
  sources: SourceRow[];
};
