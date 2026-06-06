import { useQuery } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, Columns3, Search } from "lucide-react";
import { useState } from "react";
import { api } from "../api";
import { ErrorState, PageHeader, Panel, Skeleton, formatNumber } from "../components/UI";
import { LogRow } from "../types";

type LogsResponse = { items: LogRow[]; page: number; page_size: number; total: number };

export default function DatasetExplorer() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [level, setLevel] = useState("");
  const [component, setComponent] = useState("");
  const [node, setNode] = useState("");
  const [errorCode, setErrorCode] = useState("");
  const [hour, setHour] = useState("");
  const filters = useQuery({ queryKey: ["filters"], queryFn: () => api<Record<string, string[]>>("/api/filters") });
  const query = useQuery({
    queryKey: ["logs", page, search, level, component, node, errorCode, hour],
    queryFn: () => api<LogsResponse>(`/api/logs?page=${page}&page_size=50&search=${encodeURIComponent(search)}&level=${encodeURIComponent(level)}&component=${encodeURIComponent(component)}&node_id=${encodeURIComponent(node)}&error_code=${encodeURIComponent(errorCode)}&hour=${encodeURIComponent(hour)}`)
  });
  if (query.error) return <ErrorState error={query.error} />;
  const columns: (keyof LogRow)[] = ["timestamp","level","service","component","block_id","node_id","error_code","hour","message","source_file"];
  return <div>
    <PageHeader title="Dataset Explorer" subtitle="Kibana-style exploration over the actual 10-column logs_dataset.processed_logs BigQuery schema." />
    <Panel>
      <div className="mb-4 flex flex-col gap-3 lg:flex-row">
        <div className="relative flex-1"><Search className="absolute left-3 top-2.5 text-slate-400" size={17}/><input value={search} onChange={e => {setSearch(e.target.value);setPage(1)}} className="h-10 w-full rounded-md border border-slate-200 bg-white pl-10 pr-3 text-sm dark:border-slate-700 dark:bg-slate-900" placeholder="Full text search in message"/></div>
        <select value={level} onChange={e => {setLevel(e.target.value);setPage(1)}} className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900"><option value="">All levels</option>{["INFO","WARN","WARNING","ERROR","FATAL","CRITICAL"].map(v=><option key={v}>{v}</option>)}</select>
        <select value={component} onChange={e=>{setComponent(e.target.value);setPage(1)}} className="h-10 max-w-48 rounded-md border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900"><option value="">All components</option>{filters.data?.components?.map(v=><option key={v}>{v}</option>)}</select>
        <select value={node} onChange={e=>{setNode(e.target.value);setPage(1)}} className="h-10 max-w-48 rounded-md border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900"><option value="">All nodes</option>{filters.data?.nodes?.map(v=><option key={v}>{v}</option>)}</select>
        <select value={errorCode} onChange={e=>{setErrorCode(e.target.value);setPage(1)}} className="h-10 max-w-48 rounded-md border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900"><option value="">All error codes</option>{filters.data?.error_codes?.map(v=><option key={v}>{v}</option>)}</select>
        <select value={hour} onChange={e=>{setHour(e.target.value);setPage(1)}} className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900"><option value="">All hours</option>{Array.from({length:24},(_,i)=><option key={i} value={i}>{String(i).padStart(2,"0")}:00</option>)}</select>
        <button title="Column selection uses the real schema" className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm dark:border-slate-700"><Columns3 size={16}/>10 columns</button>
      </div>
      {query.isLoading ? <Skeleton className="h-96"/> : <div className="max-h-[62vh] overflow-auto scrollbar"><table className="w-full min-w-[1500px] table-fixed text-left text-xs"><thead className="sticky top-0 z-10 bg-slate-100 dark:bg-slate-900"><tr>{columns.map(column=><th key={column} className={`${column==="message"?"w-[420px]":"w-[150px]"} border-b border-slate-200 px-3 py-2 uppercase text-slate-500 dark:border-slate-700`}>{column}</th>)}</tr></thead><tbody>{query.data?.items.map((row,index)=><tr key={`${row.timestamp}-${index}`} className="border-b border-slate-100 hover:bg-blue-50/60 dark:border-slate-800 dark:hover:bg-blue-950/20">{columns.map(column=><td key={column} className="truncate px-3 py-2" title={String(row[column] ?? "")}>{String(row[column] ?? "")}</td>)}</tr>)}</tbody></table></div>}
      <div className="mt-4 flex items-center justify-between text-sm"><span className="text-slate-500">{formatNumber(query.data?.total)} records</span><div className="flex items-center gap-2"><button className="grid h-8 w-8 place-items-center rounded border border-slate-200 disabled:opacity-40 dark:border-slate-700" disabled={page===1} onClick={()=>setPage(p=>p-1)}><ChevronLeft size={16}/></button><span>Page {page}</span><button className="grid h-8 w-8 place-items-center rounded border border-slate-200 dark:border-slate-700" onClick={()=>setPage(p=>p+1)}><ChevronRight size={16}/></button></div></div>
    </Panel>
  </div>;
}
