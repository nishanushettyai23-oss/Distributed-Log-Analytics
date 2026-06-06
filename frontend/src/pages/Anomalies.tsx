import { useQuery } from "@tanstack/react-query";
import { AlertOctagon, Gauge, Radar, TriangleAlert } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api";
import { ErrorState, Kpi, PageHeader, Panel, formatNumber } from "../components/UI";
import { useMemo, useState } from "react";

type Anomaly = { component: string; hour: number; node_id: string; error_code: string; event_count: number; anomaly_score: number; severity: string };
type Response = { summary: Record<string, number>; items: Anomaly[] };

export default function Anomalies() {
  const [search, setSearch] = useState("");
  const query = useQuery({ queryKey: ["anomalies"], queryFn: () => api<Response>("/api/anomalies") });
  const rawItems = query.data?.items || [];
  const items = useMemo(() => rawItems.filter(item => JSON.stringify(item).toLowerCase().includes(search.toLowerCase())), [rawItems, search]);
  if (query.error) return <ErrorState error={query.error} />;
  const summary = query.data?.summary || {};
  const severity = ["critical", "high", "medium"].map(name => ({ name, value: items.filter(i => i.severity === name).length }));
  return <div>
    <PageHeader title="Anomaly Detection" subtitle="Statistical deviation analysis over component activity, hourly spikes, node behavior, and rare error-code concentrations." actions={<input value={search} onChange={e=>setSearch(e.target.value)} className="h-9 rounded-md border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900" placeholder="Filter anomalies..." />} />
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <Kpi label="Anomaly Count" value={formatNumber(summary.anomaly_count)} detail="Z-score >= 2" icon={TriangleAlert} tone="amber"/>
      <Kpi label="Risk Score" value={`${formatNumber(summary.risk_score)}/100`} detail="Highest statistical deviation" icon={Gauge} tone="red"/>
      <Kpi label="Critical Events" value={formatNumber(summary.critical)} detail="Z-score >= 4" icon={AlertOctagon} tone="red"/>
      <Kpi label="High Risk Events" value={formatNumber(summary.high)} detail="Z-score >= 3" icon={Radar} tone="amber"/>
    </div>
    <div className="mt-5 grid gap-5 xl:grid-cols-3">
      <Panel title="Anomaly Timeline and Heatmap" className="h-96 xl:col-span-2"><ResponsiveContainer width="100%" height="90%"><ScatterChart><CartesianGrid opacity={0.2}/><XAxis dataKey="hour" name="Hour"/><YAxis dataKey="anomaly_score" name="Score"/><Tooltip cursor={{strokeDasharray:"3 3"}}/><Scatter data={items} fill="#dc2626"/></ScatterChart></ResponsiveContainer></Panel>
      <Panel title="Severity Distribution" className="h-96"><ResponsiveContainer width="100%" height="90%"><BarChart data={severity}><CartesianGrid opacity={0.2}/><XAxis dataKey="name"/><YAxis/><Tooltip/><Bar dataKey="value" fill="#d97706"/></BarChart></ResponsiveContainer></Panel>
      <Panel title="Detected Risk Events" className="xl:col-span-3">
        <div className="max-h-96 overflow-auto scrollbar"><table className="w-full min-w-[800px] text-left text-sm"><thead className="sticky top-0 bg-white dark:bg-slate-900"><tr>{["Severity","Score","Component","Node","Hour","Error Code","Events"].map(h => <th key={h} className="border-b border-slate-200 px-3 py-2 dark:border-slate-700">{h}</th>)}</tr></thead><tbody>{items.map((item,i) => <tr key={i} className="border-b border-slate-100 dark:border-slate-800"><td className="px-3 py-2"><span className={`rounded px-2 py-1 text-xs font-semibold ${item.severity==="critical"?"bg-red-100 text-red-700":item.severity==="high"?"bg-amber-100 text-amber-700":"bg-blue-100 text-blue-700"}`}>{item.severity}</span></td><td className="px-3 py-2 font-mono">{item.anomaly_score}</td><td className="px-3 py-2">{item.component}</td><td className="px-3 py-2">{item.node_id}</td><td className="px-3 py-2">{item.hour}</td><td className="px-3 py-2">{item.error_code}</td><td className="px-3 py-2">{item.event_count}</td></tr>)}</tbody></table></div>
      </Panel>
    </div>
  </div>;
}
