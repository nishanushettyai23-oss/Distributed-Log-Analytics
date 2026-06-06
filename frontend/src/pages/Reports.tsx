import { useState } from "react";
import { AlertCircle, CheckCircle2, Download, FileSpreadsheet, FileText, LoaderCircle, Sheet } from "lucide-react";
import { reportUrl } from "../api";
import { PageHeader, Panel } from "../components/UI";

const reports = [
  ["Executive PDF Report","KPIs, Spark status, stability metrics, and cloud processing summary","pdf",FileText],
  ["Analytics Excel Workbook","Component analytics and structured warehouse output","xlsx",FileSpreadsheet],
  ["Component CSV Export","Portable component ranking and failure concentration data","csv",Sheet]
] as const;

export default function Reports() {
  const [active,setActive]=useState<string>();
  const [message,setMessage]=useState<{type:"ok"|"error";text:string}>();

  async function download(format:"pdf"|"xlsx"|"csv") {
    setActive(format);
    setMessage(undefined);
    try {
      const response=await fetch(reportUrl(format));
      if(!response.ok) {
        const payload=await response.json().catch(()=>({}));
        throw new Error(payload.error || `Report generation failed (${response.status})`);
      }
      const blob=await response.blob();
      const disposition=response.headers.get("content-disposition") || "";
      const filename=disposition.match(/filename="?([^"]+)"?/)?.[1] || `log-analytics-report.${format}`;
      const url=URL.createObjectURL(blob);
      const anchor=document.createElement("a");
      anchor.href=url;
      anchor.download=filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      setMessage({type:"ok",text:`${format.toUpperCase()} report downloaded successfully.`});
    } catch(error) {
      setMessage({type:"error",text:error instanceof Error ? error.message : "Report download failed."});
    } finally {
      setActive(undefined);
    }
  }

  return <div><PageHeader title="Reports" subtitle="Download reproducible evidence generated from the BigQuery-backed analytics results shown in this platform."/>
    {message && <div className={`mb-5 flex items-center gap-2 rounded-md border p-3 text-sm ${message.type==="ok"?"border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950":"border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950"}`}>{message.type==="ok"?<CheckCircle2 size={18}/>:<AlertCircle size={18}/>} {message.text}</div>}
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{reports.map(([title,detail,format,Icon])=><Panel key={format}><div className="grid h-11 w-11 place-items-center rounded-lg bg-blue-100 text-blue-600 dark:bg-blue-950"><Icon/></div><h2 className="mt-5 font-semibold">{title}</h2><p className="mt-2 min-h-12 text-sm text-slate-500">{detail}</p><button type="button" disabled={Boolean(active)} onClick={()=>download(format)} className="mt-6 flex h-10 w-full items-center justify-center gap-2 rounded-md bg-blue-600 text-sm font-semibold text-white disabled:cursor-wait disabled:opacity-60">{active===format?<LoaderCircle className="animate-spin" size={16}/>:<Download size={16}/>} {active===format?"Generating...":`Download ${format.toUpperCase()}`}</button></Panel>)}</div>
  </div>;
}
