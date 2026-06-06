import { useQuery } from "@tanstack/react-query";
import { Cloud, Database, HardDrive, Server } from "lucide-react";
import { api } from "../api";
import { ErrorState, Kpi, PageHeader, Panel, formatNumber } from "../components/UI";

type Infra = { dataproc: Record<string, unknown>; storage: {buckets:{name:string;location?:string;storage_class?:string;bytes?:number|null;objects?:number|null}[]}; bigquery: {dataset:string;tables:{name:string;rows:number;bytes:number}[]}; processing: Record<string, unknown> };

export default function Infrastructure() {
  const query = useQuery({ queryKey:["infrastructure"], queryFn:()=>api<Infra>("/api/infrastructure") });
  if(query.error) return <ErrorState error={query.error}/>;
  const d=query.data?.dataproc||{}, p=query.data?.processing||{}, b=query.data?.bigquery;
  return <div><PageHeader title="Infrastructure" subtitle="Cloud operations view of Dataproc, Google Cloud Storage, BigQuery, and the latest distributed Spark execution."/>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><Kpi label="Cluster Status" value={String(d.status||"Unknown")} detail={String(d.cluster_name||"log-analytics-cluster")} icon={Server} tone="green"/><Kpi label="Worker Count" value={formatNumber(d.worker_count)} detail={String(d.machine_type||"")} icon={Cloud}/><Kpi label="Records Processed" value={formatNumber(p.records_processed)} detail="Latest Spark batch" icon={Database} tone="cyan"/><Kpi label="Processing Duration" value={String(p.duration||"Not configured")} detail="Dataproc job duration" icon={HardDrive} tone="amber"/></div>
    <div className="mt-5 grid gap-5 xl:grid-cols-2"><Panel title="Dataproc Cluster"><dl className="grid grid-cols-2 gap-4 text-sm">{Object.entries(d).map(([k,v])=><div key={k}><dt className="text-slate-500">{k.replace(/_/g," ")}</dt><dd className="mt-1 font-semibold">{String(v)}</dd></div>)}</dl></Panel><Panel title="Cloud Storage"><div className="space-y-4">{query.data?.storage.buckets.map(bucket=><div key={bucket.name} className="rounded-md border border-slate-200 p-3 text-sm dark:border-slate-700"><div className="break-all font-mono font-semibold">{bucket.name}</div><div className="mt-2 flex gap-4 text-xs text-slate-500"><span>{formatNumber(bucket.objects)} objects</span><span>{bucket.bytes ? `${(bucket.bytes/1073741824).toFixed(2)} GB` : "Size unavailable"}</span><span>{bucket.location || "Location unavailable"}</span></div></div>)}</div></Panel>
      <Panel title={`BigQuery · ${b?.dataset||"logs_dataset"}`} className="xl:col-span-2"><div className="overflow-auto"><table className="w-full text-left text-sm"><thead><tr><th className="border-b py-2 dark:border-slate-700">Table</th><th className="border-b py-2 dark:border-slate-700">Rows</th><th className="border-b py-2 dark:border-slate-700">Storage</th></tr></thead><tbody>{b?.tables.map(t=><tr key={t.name}><td className="border-b py-3 font-mono dark:border-slate-800">{t.name}</td><td className="border-b py-3 dark:border-slate-800">{formatNumber(t.rows)}</td><td className="border-b py-3 dark:border-slate-800">{(t.bytes/1073741824).toFixed(2)} GB</td></tr>)}</tbody></table></div></Panel></div>
  </div>;
}
