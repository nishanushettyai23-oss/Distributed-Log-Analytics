import { useQuery } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, CloudUpload, Columns3, LoaderCircle, Search } from "lucide-react";
import { useState } from "react";
import { api } from "../api";
import { ErrorState, PageHeader, Panel, Skeleton, formatNumber } from "../components/UI";
import { LogRow } from "../types";

type LogsResponse = { items: LogRow[]; page: number; page_size: number; total: number };
type PipelineResult = { job_id: string; status: string; input_uri: string; output_uri: string; cluster_name: string; region: string };

function optionValues(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map(item => {
    if (item && typeof item === "object") {
      const record=item as Record<string, unknown>;
      return String(record.value ?? record.name ?? "");
    }
    return String(item ?? "");
  }).filter(Boolean);
}

export default function DatasetExplorer() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [level, setLevel] = useState("");
  const [component, setComponent] = useState("");
  const [node, setNode] = useState("");
  const [errorCode, setErrorCode] = useState("");
  const [hour, setHour] = useState("");
  const [inputUri,setInputUri]=useState("gs://distributed-log-analytics-raw-logs/loghub/hdfs/full/HDFS.log");
  const [outputName,setOutputName]=useState("hdfs-full");
  const [adminToken,setAdminToken]=useState("");
  const [submitting,setSubmitting]=useState(false);
  const [pipeline,setPipeline]=useState<PipelineResult>();
  const [pipelineError,setPipelineError]=useState("");
  const filters = useQuery({ queryKey: ["filters"], queryFn: () => api<Record<string, string[]>>("/api/filters") });
  const query = useQuery({
    queryKey: ["logs", page, search, level, component, node, errorCode, hour],
    queryFn: () => api<LogsResponse>(`/api/logs?page=${page}&page_size=50&search=${encodeURIComponent(search)}&level=${encodeURIComponent(level)}&component=${encodeURIComponent(component)}&node_id=${encodeURIComponent(node)}&error_code=${encodeURIComponent(errorCode)}&hour=${encodeURIComponent(hour)}`)
  });
  if (query.error) return <ErrorState error={query.error} />;
  const columns: (keyof LogRow)[] = ["timestamp","level","service","component","block_id","node_id","error_code","hour","message","source_file"];
  const componentOptions=optionValues(filters.data?.components);
  const nodeOptions=optionValues(filters.data?.nodes);
  const errorOptions=optionValues(filters.data?.error_codes);

  async function submitPipeline() {
    setSubmitting(true); setPipelineError(""); setPipeline(undefined);
    try {
      setPipeline(await api<PipelineResult>("/api/pipeline/submit",{
        method:"POST",
        headers:{"X-Admin-Token":adminToken},
        body:JSON.stringify({input_uri:inputUri,output_name:outputName})
      }));
    } catch(error) {
      setPipelineError(error instanceof Error?error.message:"Pipeline submission failed");
    } finally {
      setSubmitting(false);
    }
  }

  return <div>
    <PageHeader title="Dataset and Batch Processing" subtitle="Inspect records already processed into BigQuery or submit an approved Cloud Storage object to the Dataproc PySpark pipeline." />
    <div className="mb-5 grid gap-5 xl:grid-cols-[1fr_0.9fr]">
      <Panel title="Deployed dataset provenance">
        <dl className="grid gap-4 text-sm sm:grid-cols-2">
          <div><dt className="text-slate-500">Source corpus</dt><dd className="mt-1 font-semibold">LogHub HDFS</dd></div>
          <div><dt className="text-slate-500">Processing mode</dt><dd className="mt-1 font-semibold">Large-scale batch</dd></div>
          <div className="sm:col-span-2"><dt className="text-slate-500">GCS input</dt><dd className="mt-1 break-all font-mono text-xs">{inputUri}</dd></div>
          <div><dt className="text-slate-500">Compute engine</dt><dd className="mt-1 font-semibold">Apache Spark on Dataproc</dd></div>
          <div><dt className="text-slate-500">Stored result</dt><dd className="mt-1 font-semibold">logs_dataset.processed_logs</dd></div>
        </dl>
      </Panel>
      <Panel title="Submit another GCS dataset">
        <div className="space-y-3">
          <label className="block text-xs font-medium text-slate-500">Input object under the raw-log bucket<input value={inputUri} onChange={e=>setInputUri(e.target.value)} className="mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 font-mono text-xs dark:border-slate-700 dark:bg-slate-900"/></label>
          <div className="grid gap-3 sm:grid-cols-2"><label className="block text-xs font-medium text-slate-500">Output name<input value={outputName} onChange={e=>setOutputName(e.target.value)} className="mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900"/></label><label className="block text-xs font-medium text-slate-500">Administrator token<input type="password" value={adminToken} onChange={e=>setAdminToken(e.target.value)} className="mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900"/></label></div>
          <button type="button" onClick={submitPipeline} disabled={submitting||!adminToken} className="flex h-10 w-full items-center justify-center gap-2 rounded-md bg-blue-600 text-sm font-semibold text-white disabled:opacity-50">{submitting?<LoaderCircle className="animate-spin" size={16}/>:<CloudUpload size={16}/>}Submit PySpark batch</button>
          {pipelineError&&<p className="text-xs text-red-600">{pipelineError}</p>}
          {pipeline&&<div className="rounded-md border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950"><div className="font-semibold">Dataproc job {pipeline.job_id} submitted</div><div className="mt-1 break-all">Output: {pipeline.output_uri}</div></div>}
          <p className="text-xs leading-5 text-slate-500">This form references data already uploaded to GCS. Browser file uploads are intentionally disabled on the public site; large files are uploaded with the documented Docker/GCS preparation tool.</p>
        </div>
      </Panel>
    </div>
    <Panel>
      <div className="mb-4 flex flex-col gap-3 lg:flex-row">
        <div className="relative flex-1"><Search className="absolute left-3 top-2.5 text-slate-400" size={17}/><input value={search} onChange={e => {setSearch(e.target.value);setPage(1)}} className="h-10 w-full rounded-md border border-slate-200 bg-white pl-10 pr-3 text-sm dark:border-slate-700 dark:bg-slate-900" placeholder="Full text search in message"/></div>
        <select value={level} onChange={e => {setLevel(e.target.value);setPage(1)}} className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900"><option value="">All levels</option>{["INFO","WARN","WARNING","ERROR","FATAL","CRITICAL"].map(v=><option key={v}>{v}</option>)}</select>
        <select value={component} onChange={e=>{setComponent(e.target.value);setPage(1)}} className="h-10 max-w-48 rounded-md border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900"><option value="">All components</option>{componentOptions.map(v=><option key={v}>{v}</option>)}</select>
        <select value={node} onChange={e=>{setNode(e.target.value);setPage(1)}} className="h-10 max-w-48 rounded-md border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900"><option value="">All nodes</option>{nodeOptions.map(v=><option key={v}>{v}</option>)}</select>
        <select value={errorCode} onChange={e=>{setErrorCode(e.target.value);setPage(1)}} className="h-10 max-w-48 rounded-md border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900"><option value="">All error codes</option>{errorOptions.map(v=><option key={v}>{v}</option>)}</select>
        <select value={hour} onChange={e=>{setHour(e.target.value);setPage(1)}} className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm dark:border-slate-700 dark:bg-slate-900"><option value="">All hours</option>{Array.from({length:24},(_,i)=><option key={i} value={i}>{String(i).padStart(2,"0")}:00</option>)}</select>
        <button title="Column selection uses the real schema" className="flex h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm dark:border-slate-700"><Columns3 size={16}/>10 columns</button>
      </div>
      {query.isLoading ? <Skeleton className="h-96"/> : <div className="max-h-[62vh] overflow-auto scrollbar"><table className="w-full min-w-[1500px] table-fixed text-left text-xs"><thead className="sticky top-0 z-10 bg-slate-100 dark:bg-slate-900"><tr>{columns.map(column=><th key={column} className={`${column==="message"?"w-[420px]":"w-[150px]"} border-b border-slate-200 px-3 py-2 uppercase text-slate-500 dark:border-slate-700`}>{column}</th>)}</tr></thead><tbody>{query.data?.items.map((row,index)=><tr key={`${row.timestamp}-${index}`} className="border-b border-slate-100 hover:bg-blue-50/60 dark:border-slate-800 dark:hover:bg-blue-950/20">{columns.map(column=><td key={column} className="truncate px-3 py-2" title={String(row[column] ?? "")}>{String(row[column] ?? "")}</td>)}</tr>)}</tbody></table></div>}
      <div className="mt-4 flex items-center justify-between text-sm"><span className="text-slate-500">{formatNumber(query.data?.total)} records</span><div className="flex items-center gap-2"><button className="grid h-8 w-8 place-items-center rounded border border-slate-200 disabled:opacity-40 dark:border-slate-700" disabled={page===1} onClick={()=>setPage(p=>p-1)}><ChevronLeft size={16}/></button><span>Page {page}</span><button className="grid h-8 w-8 place-items-center rounded border border-slate-200 dark:border-slate-700" onClick={()=>setPage(p=>p+1)}><ChevronRight size={16}/></button></div></div>
    </Panel>
  </div>;
}
