import { motion } from "framer-motion";
import { AlertCircle, ArrowUpRight, LucideIcon } from "lucide-react";
import { ReactNode } from "react";

export function PageHeader({ title, subtitle, actions }: { title: string; subtitle: string; actions?: ReactNode }) {
  return <div className="mb-6 flex flex-col justify-between gap-3 sm:flex-row sm:items-end"><div><h1 className="text-2xl font-bold sm:text-3xl">{title}</h1><p className="mt-1 max-w-3xl text-sm text-slate-500 dark:text-slate-400">{subtitle}</p></div>{actions}</div>;
}

export function Panel({ title, children, className = "" }: { title?: string; children: ReactNode; className?: string }) {
  return <section className={`glass rounded-lg p-4 ${className}`}>{title && <h2 className="mb-4 text-sm font-semibold">{title}</h2>}{children}</section>;
}

export function Kpi({ label, value, detail, icon: Icon, tone = "blue" }: { label: string; value: string | number; detail: string; icon: LucideIcon; tone?: string }) {
  const tones: Record<string, string> = { blue: "text-blue-600 bg-blue-100 dark:bg-blue-950", green: "text-emerald-600 bg-emerald-100 dark:bg-emerald-950", amber: "text-amber-600 bg-amber-100 dark:bg-amber-950", red: "text-red-600 bg-red-100 dark:bg-red-950", cyan: "text-cyan-600 bg-cyan-100 dark:bg-cyan-950" };
  return <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="glass metric-gradient min-h-36 rounded-lg p-4">
    <div className="flex items-start justify-between"><div className={`grid h-9 w-9 place-items-center rounded-lg ${tones[tone] || tones.blue}`}><Icon size={18} /></div><div className="flex items-center gap-1 text-xs font-medium text-emerald-600"><ArrowUpRight size={14} />Cloud</div></div>
    <div className="mt-4 text-2xl font-bold">{value}</div><div className="mt-1 text-sm font-medium">{label}</div><div className="mt-1 text-xs text-slate-500">{detail}</div>
  </motion.div>;
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-slate-200 dark:bg-slate-700 ${className}`} />;
}

export function ErrorState({ error }: { error: Error }) {
  return <div className="glass flex items-start gap-3 rounded-lg border-red-200 p-5 text-red-700 dark:border-red-900 dark:text-red-300"><AlertCircle className="mt-0.5" /><div><div className="font-semibold">Cloud data unavailable</div><div className="mt-1 text-sm">{error.message}</div><div className="mt-2 text-xs opacity-75">Configure Google Application Default Credentials and BigQuery access for logs_dataset.processed_logs.</div></div></div>;
}

export function formatNumber(value: unknown) {
  const number = Number(value || 0);
  return Intl.NumberFormat("en-US", { notation: number > 999999 ? "compact" : "standard", maximumFractionDigits: 1 }).format(number);
}

export const chartColors = ["#2563eb", "#0891b2", "#059669", "#d97706", "#dc2626", "#7c3aed", "#475467"];
