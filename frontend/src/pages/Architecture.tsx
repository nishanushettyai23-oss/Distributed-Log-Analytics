import { useCallback, useState } from "react";
import ReactFlow, { Background, Controls, Edge, Node, NodeMouseHandler, Position } from "reactflow";
import "reactflow/dist/style.css";
import { Database, LockKeyhole, Server, Workflow } from "lucide-react";
import { PageHeader, Panel } from "../components/UI";

const initialNodes: Node[] = [
  {id:"dataset",position:{x:0,y:120},data:{label:"LogHub HDFS\n10.68M records"},sourcePosition:Position.Right,targetPosition:Position.Left,type:"default"},
  {id:"gcs",position:{x:220,y:120},data:{label:"Google Cloud Storage\nRaw object storage"},sourcePosition:Position.Right,targetPosition:Position.Left},
  {id:"dataproc",position:{x:440,y:120},data:{label:"Dataproc Cluster\n1 master + 2 workers"},sourcePosition:Position.Right,targetPosition:Position.Left},
  {id:"spark",position:{x:660,y:120},data:{label:"Apache Spark\nDistributed analytics"},sourcePosition:Position.Right,targetPosition:Position.Left},
  {id:"bigquery",position:{x:880,y:120},data:{label:"BigQuery Warehouse\nprocessed_logs"},sourcePosition:Position.Right,targetPosition:Position.Left},
  {id:"flask",position:{x:1100,y:120},data:{label:"Flask REST API\nService + repository"},sourcePosition:Position.Right,targetPosition:Position.Left},
  {id:"nginx",position:{x:1320,y:120},data:{label:"Nginx on Compute Engine\nDocker reverse proxy"},sourcePosition:Position.Right,targetPosition:Position.Left},
  {id:"react",position:{x:1540,y:120},data:{label:"React Dashboard\nCloud analytics UI"},sourcePosition:Position.Right,targetPosition:Position.Left},
  {id:"caddy",position:{x:1760,y:120},data:{label:"Caddy HTTPS Gateway\nTLS on ports 80/443"},sourcePosition:Position.Right,targetPosition:Position.Left},
  {id:"users",position:{x:1980,y:120},data:{label:"External Users\nSecure public URL"},sourcePosition:Position.Right,targetPosition:Position.Left}
];
const edges: Edge[] = initialNodes.slice(0,-1).map((n,i)=>({id:`e${i}`,source:n.id,target:initialNodes[i+1].id,animated:true,style:{stroke:"#2563eb",strokeWidth:2}}));
const details: Record<string,string> = {
  dataset:"LogHub HDFS source corpus. The deployed BigQuery table currently contains 10,685,241 processed records.",
  gcs:"Durable cloud object storage for raw HDFS logs, Spark code, and Parquet output.",
  dataproc:"Managed Spark infrastructure in us-central1 with distributed worker execution.",
  spark:"Parses the real HDFS schema, extracts component/node/error features, aggregates metrics, and computes anomalies.",
  bigquery:"Analytical warehouse using logs_dataset.processed_logs and its ten real columns.",
  flask:"Read-only APIs, query safety, pagination, caching, infrastructure metadata, and exports.",
  nginx:"Nginx serves the compiled React application and forwards /api requests to the Flask container. Both containers run with Docker Compose on Compute Engine.",
  react:"Responsive React/TypeScript visualization layer with charts, explorers, reports, and architecture inspection.",
  caddy:"The public gateway obtains and renews the TLS certificate, redirects HTTP to HTTPS, and forwards secure traffic to the internal Nginx frontend.",
  users:"Administrators, DevOps engineers, and evaluators access the deployed dashboard through one secure HTTPS address."
};

export default function Architecture() {
  const [selected,setSelected]=useState("dataset");
  const onNodeClick:NodeMouseHandler=useCallback((_,node)=>setSelected(node.id),[]);
  return <div><PageHeader title="Cloud Architecture" subtitle="The system separates one-time distributed batch processing from the continuously available web application that reads the stored results."/>
    <div className="mb-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {[
        [Database,"Data layer","Raw HDFS logs in GCS; structured results in BigQuery"],
        [Workflow,"Compute layer","Spark distributes parsing and aggregation across Dataproc workers"],
        [Server,"Application layer","Flask and React run as Docker containers on Compute Engine"],
        [LockKeyhole,"Access layer","Caddy terminates HTTPS; Nginx serves React and proxies /api"]
      ].map(([Icon,title,text])=><div key={String(title)} className="border-t-2 border-blue-500 bg-white/60 p-4 dark:bg-slate-900/50"><Icon className="text-blue-600" size={20}/><h2 className="mt-3 text-sm font-semibold">{String(title)}</h2><p className="mt-1 text-xs leading-5 text-slate-500">{String(text)}</p></div>)}
    </div>
    <div className="grid gap-5 xl:grid-cols-[1fr_320px]"><Panel className="h-[560px] overflow-hidden p-0"><ReactFlow nodes={initialNodes} edges={edges} onNodeClick={onNodeClick} fitView minZoom={0.35}><Background/><Controls/></ReactFlow></Panel><Panel title={initialNodes.find(n=>n.id===selected)?.data.label.split("\n")[0]}><p className="text-sm leading-6 text-slate-600 dark:text-slate-300">{details[selected]}</p><div className="mt-5 border-t border-slate-200 pt-4 text-xs text-slate-500 dark:border-slate-700">Select a node to inspect its role in the deployed batch analytics architecture.</div></Panel></div>
    <section className="mt-5 grid gap-5 lg:grid-cols-2">
      <Panel title="Batch analytics path"><ol className="space-y-3 text-sm text-slate-600 dark:text-slate-300">{["Store the LogHub HDFS corpus in Cloud Storage.","Submit the PySpark job to a 1-master, 2-worker Dataproc cluster.","Parse logs, extract features, aggregate failures, and calculate anomaly indicators.","Write durable analytics tables and Parquet output to BigQuery and GCS."].map((step,index)=><li key={step} className="flex gap-3"><span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-blue-600 text-xs font-bold text-white">{index+1}</span><span className="pt-0.5">{step}</span></li>)}</ol></Panel>
      <Panel title="Serving and security path"><ol className="space-y-3 text-sm text-slate-600 dark:text-slate-300">{["An external user opens the HTTPS project address.","Caddy manages the TLS certificate and forwards traffic to Nginx.","Nginx serves React and proxies API requests to Flask inside Docker Compose.","Flask performs read-only BigQuery and cloud metadata queries for the dashboard."].map((step,index)=><li key={step} className="flex gap-3"><span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-emerald-600 text-xs font-bold text-white">{index+1}</span><span className="pt-0.5">{step}</span></li>)}</ol></Panel>
    </section>
  </div>;
}
