import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, Boxes, Clock, Database, HardDrive, Server, Workflow } from "lucide-react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api";
import { ErrorState, Kpi, PageHeader, Panel, Skeleton, chartColors, formatNumber } from "../components/UI";
import { AnalyticsResponse, OverviewResponse } from "../types";

export default function Dashboard() {
  const overview = useQuery({ queryKey: ["overview"], queryFn: () => api<OverviewResponse>("/api/overview") });
  const analytics = useQuery({ queryKey: ["analytics"], queryFn: () => api<AnalyticsResponse>("/api/analytics") });
  if (overview.error) return <ErrorState error={overview.error} />;
  const m = overview.data?.metrics || {};

  return <div>
    <PageHeader title="Executive Dashboard" subtitle="Enterprise visibility into 10.6M+ HDFS records processed by Apache Spark on Google Cloud Dataproc." actions={<div className="text-xs text-slate-500">Last updated {m.updated_at ? new Date(String(m.updated_at)).toLocaleTimeString() : "waiting for cloud"}</div>} />
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {overview.isLoading ? Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-36" />) : <>
        <Kpi label="Total Logs Processed" value={formatNumber(m.total_logs)} detail="logs_dataset.processed_logs" icon={Database} />
        <Kpi label="Total Components" value={formatNumber(m.total_components)} detail="Distinct Spark-extracted components" icon={Boxes} tone="cyan" />
        <Kpi label="Unique Nodes" value={formatNumber(m.total_nodes)} detail="Infrastructure nodes observed" icon={Server} tone="green" />
        <Kpi label="Error Codes" value={formatNumber(m.total_error_codes)} detail="Distinct classified error signatures" icon={AlertTriangle} tone="amber" />
        <Kpi label="Dataproc Workers" value={formatNumber(m.dataproc_workers)} detail="Distributed Spark executors" icon={Workflow} />
        <Kpi label="BigQuery Table Size" value={m.bigquery_table_size_bytes ? `${(Number(m.bigquery_table_size_bytes) / 1073741824).toFixed(2)} GB` : "Querying"} detail="Analytical warehouse footprint" icon={HardDrive} tone="cyan" />
        <Kpi label="Processing Duration" value={String(m.processing_duration || "Not configured")} detail="Latest full Spark batch" icon={Clock} tone="green" />
        <Kpi label="Spark Job Status" value={String(m.last_spark_job_status || "Unknown")} detail="Latest Dataproc execution" icon={Activity} tone="green" />
      </>}
    </div>

    <div className="mt-5 grid gap-5 xl:grid-cols-3">
      <Panel title="Hourly Activity Trend" className="xl:col-span-2 h-80">
        <ResponsiveContainer width="100%" height="90%"><AreaChart data={analytics.data?.hourly_activity || []}><defs><linearGradient id="activity" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#2563eb" stopOpacity={0.35}/><stop offset="95%" stopColor="#2563eb" stopOpacity={0}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" opacity={0.2}/><XAxis dataKey="hour"/><YAxis width={46}/><Tooltip/><Area type="monotone" dataKey="logs" stroke="#2563eb" fill="url(#activity)" strokeWidth={2}/><Area type="monotone" dataKey="failures" stroke="#dc2626" fill="transparent" strokeWidth={2}/></AreaChart></ResponsiveContainer>
      </Panel>
      <Panel title="Dataset Composition" className="h-80">
        <ResponsiveContainer width="100%" height="90%"><PieChart><Pie data={analytics.data?.levels || []} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={3}>{(analytics.data?.levels || []).map((_, i) => <Cell key={i} fill={chartColors[i % chartColors.length]} />)}</Pie><Tooltip/></PieChart></ResponsiveContainer>
      </Panel>
      <Panel title="Top Components" className="xl:col-span-2 h-80">
        <ResponsiveContainer width="100%" height="90%"><BarChart data={analytics.data?.components || []} layout="vertical"><CartesianGrid strokeDasharray="3 3" opacity={0.2}/><XAxis type="number"/><YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 11 }}/><Tooltip/><Bar dataKey="value" fill="#0891b2" radius={[0,4,4,0]}/></BarChart></ResponsiveContainer>
      </Panel>
      <Panel title="Derived Health Metrics" className="h-80">
        <div className="space-y-5 pt-3">
          {[
            ["System Stability Index", Number(m.system_stability_index || 0), "#059669"],
            ["Error Density", Number(m.error_density || 0), "#dc2626"],
            ["Processing Efficiency", Math.min(100, Number(m.processing_efficiency || 0) / 100000), "#2563eb"]
          ].map(([label, value, color]) => <div key={String(label)}><div className="mb-2 flex justify-between text-sm"><span>{label}</span><span className="font-semibold">{Number(value).toFixed(1)}%</span></div><div className="h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700"><div className="h-full rounded-full transition-all" style={{ width: `${Math.min(Number(value), 100)}%`, background: String(color) }} /></div></div>)}
        </div>
      </Panel>
    </div>
  </div>;
}
