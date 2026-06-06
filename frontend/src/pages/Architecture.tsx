import { useCallback, useState } from "react";
import ReactFlow, { Background, Controls, Edge, Node, NodeMouseHandler, Position } from "reactflow";
import "reactflow/dist/style.css";
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
  {id:"users",position:{x:1760,y:120},data:{label:"External Users\nPublic port 3000"},sourcePosition:Position.Right,targetPosition:Position.Left}
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
  users:"Administrators, DevOps engineers, and evaluators access the deployed dashboard through the Compute Engine external IP on TCP port 3000."
};

export default function Architecture() {
  const [selected,setSelected]=useState("dataset");
  const onNodeClick:NodeMouseHandler=useCallback((_,node)=>setSelected(node.id),[]);
  return <div><PageHeader title="Cloud Architecture" subtitle="Large-scale batch pipeline from LogHub storage and Dataproc processing to the public Dockerized analytics dashboard."/><div className="grid gap-5 xl:grid-cols-[1fr_320px]"><Panel className="h-[620px] overflow-hidden p-0"><ReactFlow nodes={initialNodes} edges={edges} onNodeClick={onNodeClick} fitView minZoom={0.35}><Background/><Controls/></ReactFlow></Panel><Panel title={initialNodes.find(n=>n.id===selected)?.data.label.split("\n")[0]}><p className="text-sm leading-6 text-slate-600 dark:text-slate-300">{details[selected]}</p><div className="mt-5 border-t border-slate-200 pt-4 text-xs text-slate-500 dark:border-slate-700">Select a node to inspect its role in the deployed batch analytics architecture.</div></Panel></div></div>;
}
