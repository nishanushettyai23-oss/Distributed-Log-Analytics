import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, ArrowRight, Boxes, Clock, Database, HardDrive, SearchCheck, Server, ShieldCheck, Workflow } from "lucide-react";
import { Link } from "react-router-dom";
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
    <PageHeader title="Distributed Log Analytics" subtitle="A large-scale batch analytics system that turns raw HDFS infrastructure logs into searchable operational evidence and anomaly insights." actions={<div className="text-xs text-slate-500">Last updated {m.updated_at ? new Date(String(m.updated_at)).toLocaleTimeString() : "waiting for cloud"}</div>} />

    <section className="mb-5 grid gap-5 border-y border-slate-200 py-5 dark:border-slate-700 xl:grid-cols-[1.15fr_0.85fr]">
      <div>
        <div className="text-xs font-semibold uppercase text-blue-600">Project purpose</div>
        <h2 className="mt-2 max-w-3xl text-xl font-bold">Find failure patterns in millions of machine-generated records without processing them on one computer.</h2>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600 dark:text-slate-300">The LogHub HDFS dataset is stored in Google Cloud Storage and processed as a batch by Apache Spark on Dataproc. Parsed events and aggregate results are written to BigQuery, where this dashboard queries error trends, components, nodes, and statistical anomalies.</p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link to="/architecture" className="inline-flex h-10 items-center gap-2 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white">Explore architecture <ArrowRight size={16}/></Link>
          <Link to="/logs" className="inline-flex h-10 items-center gap-2 rounded-md border border-slate-300 px-4 text-sm font-semibold dark:border-slate-600">Inspect analytics <SearchCheck size={16}/></Link>
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
        {[
          [Database, "Input", "10.68M HDFS log records in GCS"],
          [Workflow, "Processing", "Distributed Spark batch on Dataproc"],
          [ShieldCheck, "Outcome", "Queryable metrics and anomaly evidence"]
        ].map(([Icon,label,detail])=><div key={String(label)} className="flex min-h-20 items-center gap-3 border-l-2 border-blue-500 bg-white/60 px-4 dark:bg-slate-900/50"><div className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-blue-100 text-blue-600 dark:bg-blue-950"><Icon size={18}/></div><div><div className="text-xs font-semibold uppercase text-slate-400">{String(label)}</div><div className="mt-1 text-sm font-medium">{String(detail)}</div></div></div>)}
      </div>
    </section>

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
