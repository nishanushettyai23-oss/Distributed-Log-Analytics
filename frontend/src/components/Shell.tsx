import { ReactNode, useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import {
  Activity, AlertTriangle, Boxes, ChevronRight, CloudCog, Database,
  FileBarChart, Menu, Moon, Network, Search, Server, Sun, X
} from "lucide-react";

const nav = [
  ["/", "Executive Dashboard", Activity],
  ["/logs", "Log Analytics", FileBarChart],
  ["/anomalies", "Anomaly Detection", AlertTriangle],
  ["/dataset", "Dataset Explorer", Database],
  ["/bigquery", "BigQuery Explorer", Boxes],
  ["/infrastructure", "Infrastructure", Server],
  ["/architecture", "Architecture", Network],
  ["/reports", "Reports", CloudCog]
] as const;

export default function Shell({ children }: { children: ReactNode }) {
  const [dark, setDark] = useState(() => localStorage.theme === "dark");
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.theme = dark ? "dark" : "light";
  }, [dark]);

  const sidebar = (
    <aside className="flex h-full w-72 flex-col border-r border-slate-200 bg-white/90 p-4 dark:border-slate-700 dark:bg-slate-950/95">
      <div className="flex h-14 items-center gap-3 px-2">
        <div className="grid h-10 w-10 place-items-center rounded-lg bg-blue-600 text-white"><Activity size={22} /></div>
        <div><div className="font-bold text-slate-900 dark:text-white">Cloud Observability</div><div className="text-xs text-slate-500">Spark + BigQuery</div></div>
      </div>
      <div className="mt-5 px-2 text-xs font-semibold uppercase text-slate-400">Analytics Platform</div>
      <nav className="mt-2 space-y-1">
        {nav.map(([path, label, Icon]) => (
          <NavLink
            key={path}
            to={path}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) => `flex h-11 items-center gap-3 rounded-lg px-3 text-sm font-medium transition ${
              isActive ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20" : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
            }`}
          >
            <Icon size={18} /><span className="flex-1">{label}</span><ChevronRight size={15} className="opacity-60" />
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto rounded-lg border border-emerald-200 bg-emerald-50 p-3 dark:border-emerald-900 dark:bg-emerald-950/40">
        <div className="flex items-center gap-2 text-sm font-semibold text-emerald-700 dark:text-emerald-300"><span className="h-2 w-2 rounded-full bg-emerald-500" />Cloud pipeline</div>
        <div className="mt-1 text-xs text-emerald-700/70 dark:text-emerald-300/70">10,685,241 records processed</div>
      </div>
    </aside>
  );

  return (
    <div className="app-bg min-h-screen text-slate-900 transition-colors dark:text-slate-100">
      <div className="fixed inset-y-0 left-0 z-30 hidden lg:block">{sidebar}</div>
      {mobileOpen && <div className="fixed inset-0 z-40 bg-black/40 lg:hidden" onClick={() => setMobileOpen(false)}><div className="h-full" onClick={e => e.stopPropagation()}>{sidebar}</div></div>}
      <div className="lg:pl-72">
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-slate-200 bg-white/80 px-4 backdrop-blur-xl dark:border-slate-700 dark:bg-slate-950/80 sm:px-6">
          <button className="grid h-9 w-9 place-items-center rounded-md hover:bg-slate-100 dark:hover:bg-slate-800 lg:hidden" onClick={() => setMobileOpen(v => !v)}>{mobileOpen ? <X /> : <Menu />}</button>
          <div className="relative max-w-xl flex-1">
            <Search className="absolute left-3 top-2.5 text-slate-400" size={17} />
            <input className="h-10 w-full rounded-lg border border-slate-200 bg-slate-50 pl-10 pr-3 text-sm outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-900" placeholder="Search logs, components, nodes, error codes..." />
          </div>
          <div className="hidden items-center gap-2 text-xs text-slate-500 sm:flex"><span className="h-2 w-2 rounded-full bg-emerald-500" />Auto refresh 60s</div>
          <button title="Toggle theme" className="grid h-9 w-9 place-items-center rounded-md border border-slate-200 dark:border-slate-700" onClick={() => setDark(v => !v)}>{dark ? <Sun size={17} /> : <Moon size={17} />}</button>
        </header>
        <main className="p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
}
