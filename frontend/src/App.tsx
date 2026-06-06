import { AnimatePresence, motion } from "framer-motion";
import { lazy, Suspense } from "react";
import { Route, Routes, useLocation } from "react-router-dom";
import Shell from "./components/Shell";
import { Skeleton } from "./components/UI";

const Architecture = lazy(() => import("./pages/Architecture"));
const BigQueryExplorer = lazy(() => import("./pages/BigQueryExplorer"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const DatasetExplorer = lazy(() => import("./pages/DatasetExplorer"));
const Infrastructure = lazy(() => import("./pages/Infrastructure"));
const LogAnalytics = lazy(() => import("./pages/LogAnalytics"));
const Anomalies = lazy(() => import("./pages/Anomalies"));
const Reports = lazy(() => import("./pages/Reports"));

export default function App() {
  const location = useLocation();
  return <Shell><AnimatePresence mode="wait"><motion.div key={location.pathname} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -4 }} transition={{ duration: 0.2 }}><Suspense fallback={<div className="space-y-4"><Skeleton className="h-10 w-72"/><Skeleton className="h-40"/><Skeleton className="h-80"/></div>}><Routes location={location}>
    <Route path="/" element={<Dashboard />} />
    <Route path="/logs" element={<LogAnalytics />} />
    <Route path="/anomalies" element={<Anomalies />} />
    <Route path="/dataset" element={<DatasetExplorer />} />
    <Route path="/bigquery" element={<BigQueryExplorer />} />
    <Route path="/infrastructure" element={<Infrastructure />} />
    <Route path="/architecture" element={<Architecture />} />
    <Route path="/reports" element={<Reports />} />
  </Routes></Suspense></motion.div></AnimatePresence></Shell>;
}
