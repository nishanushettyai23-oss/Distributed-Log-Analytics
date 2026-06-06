import Editor from "@monaco-editor/react";
import { useQuery } from "@tanstack/react-query";
import { Clock, Download, Play, Rows3 } from "lucide-react";
import { useState } from "react";
import { api } from "../api";
import { PageHeader, Panel, formatNumber } from "../components/UI";

const initialSql = `SELECT
  component,
  COUNT(*) AS log_count,
  COUNTIF(UPPER(level) IN ('ERROR', 'FATAL', 'CRITICAL')) AS failures
FROM \`distributed-log-analytics.logs_dataset.processed_logs\`
GROUP BY component
ORDER BY log_count DESC
LIMIT 25`;

type QueryResult = { rows: Record<string, unknown>[]; duration_ms: number; returned_rows: number; bytes_processed: number; job_id: string };

export default function BigQueryExplorer() {
  const [sql, setSql] = useState(initialSql);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);
  const history = useQuery({ queryKey: ["query-history"], queryFn: () => api<Record<string, unknown>[]>("/api/query/history") });
  async function execute() {
    setRunning(true); setError("");
    try { setResult(await api<QueryResult>("/api/query", { method: "POST", body: JSON.stringify({ sql }) })); history.refetch(); }
    catch (e) { setError(e instanceof Error ? e.message : "Query failed"); }
    finally { setRunning(false); }
  }
  async function exportResult(format: "csv" | "xlsx") {
    setError("");
    try {
      const response = await fetch(`/api/query/export/${format}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sql })
      });
      if (!response.ok) {
        const payload = await response.json();
        throw new Error(payload.error || "Export failed");
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `bigquery-results.${format}`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Export failed");
    }
  }
  const columns = result?.rows[0] ? Object.keys(result.rows[0]) : [];
  return <div>
    <PageHeader title="BigQuery Explorer" subtitle="Read-only SQL workspace for logs_dataset.processed_logs. INSERT, UPDATE, DELETE, DROP, ALTER, and CREATE are blocked." actions={<button onClick={execute} disabled={running} className="flex h-10 items-center gap-2 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white disabled:opacity-50"><Play size={16}/>{running?"Executing":"Run query"}</button>} />
    <div className="grid gap-5 xl:grid-cols-[1fr_300px]">
      <div className="space-y-5">
        <Panel><div className="overflow-hidden rounded-md border border-slate-700"><Editor height="340px" language="sql" theme="vs-dark" value={sql} onChange={v=>setSql(v||"")} options={{ minimap:{enabled:false}, fontSize:14, padding:{top:16}, automaticLayout:true }}/></div></Panel>
        {error && <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">{error}</div>}
        {result && <Panel title="Query Results">
          <div className="mb-4 flex flex-wrap items-center gap-4 text-xs text-slate-500"><span className="flex gap-1"><Clock size={14}/>{result.duration_ms} ms</span><span className="flex gap-1"><Rows3 size={14}/>{result.returned_rows} rows</span><span>{formatNumber(result.bytes_processed)} bytes processed</span><span>Job {result.job_id}</span><button onClick={()=>exportResult("csv")} className="ml-auto flex items-center gap-1 rounded border px-2 py-1 dark:border-slate-700"><Download size={13}/>CSV</button><button onClick={()=>exportResult("xlsx")} className="flex items-center gap-1 rounded border px-2 py-1 dark:border-slate-700"><Download size={13}/>Excel</button></div>
          <div className="max-h-96 overflow-auto scrollbar"><table className="w-full min-w-[700px] text-left text-xs"><thead><tr>{columns.map(c=><th key={c} className="border-b px-3 py-2 dark:border-slate-700">{c}</th>)}</tr></thead><tbody>{result.rows.map((row,i)=><tr key={i} className="border-b dark:border-slate-800">{columns.map(c=><td key={c} className="max-w-xs truncate px-3 py-2">{String(row[c]??"")}</td>)}</tr>)}</tbody></table></div>
        </Panel>}
      </div>
      <Panel title="Query History"><div className="space-y-3">{history.data?.map((item,i)=><button key={i} className="w-full rounded-md border border-slate-200 p-3 text-left text-xs hover:border-blue-400 dark:border-slate-700" onClick={()=>setSql(String(item.sql))}><div className="line-clamp-3 font-mono">{String(item.sql)}</div><div className="mt-2 text-slate-500">{String(item.duration_ms)} ms · {String(item.returned_rows)} rows</div></button>)}{!history.data?.length&&<p className="text-sm text-slate-500">Executed SELECT queries appear here.</p>}</div></Panel>
    </div>
  </div>;
}
