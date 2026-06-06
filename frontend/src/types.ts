export type OverviewResponse = {
  metrics: Record<string, number | string | null>;
};

export type ChartItem = {
  name?: string;
  hour?: number;
  value?: number;
  logs?: number;
  failures?: number;
};

export type AnalyticsResponse = {
  hourly_activity: ChartItem[];
  levels: ChartItem[];
  components: ChartItem[];
  nodes: ChartItem[];
  error_codes: ChartItem[];
};

export type LogRow = {
  timestamp: string;
  level: string;
  service: string;
  component: string;
  block_id: string;
  node_id: string;
  error_code: string;
  hour: number;
  message: string;
  source_file: string;
};
