import { Download, FileSpreadsheet, FileText, Sheet } from "lucide-react";
import { reportUrl } from "../api";
import { PageHeader, Panel } from "../components/UI";

const reports = [
  ["Executive PDF Report","KPIs, Spark status, stability metrics, and cloud processing summary","pdf",FileText],
  ["Analytics Excel Workbook","Component analytics and structured warehouse output","xlsx",FileSpreadsheet],
  ["Component CSV Export","Portable component ranking and failure concentration data","csv",Sheet]
] as const;

export default function Reports() {
  return <div><PageHeader title="Reports" subtitle="Generate portable evidence packages for analytics, infrastructure, anomaly summaries, and cloud processing metrics."/><div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{reports.map(([title,detail,format,Icon])=><Panel key={format}><div className="grid h-11 w-11 place-items-center rounded-lg bg-blue-100 text-blue-600 dark:bg-blue-950"><Icon/></div><h2 className="mt-5 font-semibold">{title}</h2><p className="mt-2 min-h-12 text-sm text-slate-500">{detail}</p><a className="mt-6 flex h-10 items-center justify-center gap-2 rounded-md bg-blue-600 text-sm font-semibold text-white" href={reportUrl(format)}><Download size={16}/>Download {format.toUpperCase()}</a></Panel>)}</div></div>;
}
