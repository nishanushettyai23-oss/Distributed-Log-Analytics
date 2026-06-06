import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api";
import { ErrorState, PageHeader, Panel, chartColors } from "../components/UI";
import { AnalyticsResponse } from "../types";

export default function LogAnalytics() {
  const query = useQuery({ queryKey: ["analytics"], queryFn: () => api<AnalyticsResponse>("/api/analytics") });
  if (query.error) return <ErrorState error={query.error} />;
  const data = query.data;
  return <div>
    <PageHeader title="Log Analytics" subtitle="Distributed component, node, temporal, and error-code analytics generated from the real BigQuery processed_logs schema." />
    <div className="grid gap-5 xl:grid-cols-2">
      <Panel title="Log Distribution" className="h-80"><ResponsiveContainer width="100%" height="90%"><PieChart><Pie data={data?.levels || []} dataKey="value" nameKey="name" innerRadius={55} outerRadius={95}>{(data?.levels || []).map((_, i) => <Cell key={i} fill={chartColors[i % chartColors.length]}/>)}</Pie><Tooltip/></PieChart></ResponsiveContainer></Panel>
      <Panel title="Component Analysis" className="h-80"><ResponsiveContainer width="100%" height="90%"><BarChart data={data?.components || []}><CartesianGrid opacity={0.2}/><XAxis dataKey="name" angle={-25} textAnchor="end" height={70} tick={{fontSize:10}}/><YAxis/><Tooltip/><Bar dataKey="value" stackId="a" fill="#2563eb"/><Bar dataKey="failures" stackId="a" fill="#dc2626"/></BarChart></ResponsiveContainer></Panel>
      <Panel title="Hourly Activity Trend" className="h-80"><ResponsiveContainer width="100%" height="90%"><LineChart data={data?.hourly_activity || []}><CartesianGrid opacity={0.2}/><XAxis dataKey="hour"/><YAxis/><Tooltip/><Line dataKey="logs" stroke="#0891b2" strokeWidth={2}/><Line dataKey="failures" stroke="#dc2626" strokeWidth={2}/></LineChart></ResponsiveContainer></Panel>
      <Panel title="Top Active Nodes" className="h-80"><ResponsiveContainer width="100%" height="90%"><BarChart data={data?.nodes || []} layout="vertical"><CartesianGrid opacity={0.2}/><XAxis type="number"/><YAxis type="category" dataKey="name" width={130} tick={{fontSize:10}}/><Tooltip/><Bar dataKey="value" fill="#059669" radius={[0,4,4,0]}/></BarChart></ResponsiveContainer></Panel>
      <Panel title="Error Code Frequency" className="h-80 xl:col-span-2"><ResponsiveContainer width="100%" height="90%"><BarChart data={data?.error_codes || []}><CartesianGrid opacity={0.2}/><XAxis dataKey="name"/><YAxis/><Tooltip/><Bar dataKey="value" fill="#d97706" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer></Panel>
    </div>
  </div>;
}
