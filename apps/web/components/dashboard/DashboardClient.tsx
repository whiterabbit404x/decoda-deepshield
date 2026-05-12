"use client";

import { useMemo, useState } from "react";

import { AlertsList } from "@/components/dashboard/AlertsList";
import { RiskTrendChart } from "@/components/dashboard/ChartPanel";
import { DataTables } from "@/components/dashboard/DataTables";
import { StatCards } from "@/components/dashboard/StatCards";
import { UploadPanel } from "@/components/dashboard/UploadPanel";
import { getAlerts, getIncidents, getRuntimeStatus } from "@/lib/api";
import { type Alert, type DetectionOutput, type HealthResponse, type Incident, type RuntimeStatus } from "@/types/api";

interface DashboardClientProps { health: HealthResponse | null; runtimeStatus: RuntimeStatus | null; alerts: Alert[]; incidents: Incident[]; alertsError?: string; incidentsError?: string; }

export function DashboardClient({ health, runtimeStatus, alerts: initialAlerts, incidents: initialIncidents, alertsError: initialAlertsError, incidentsError: initialIncidentsError }: DashboardClientProps) {
  const [detections, setDetections] = useState<DetectionOutput[]>([]);
  const [alerts, setAlerts] = useState(initialAlerts);
  const [incidents, setIncidents] = useState(initialIncidents);
  const [alertsError, setAlertsError] = useState(initialAlertsError);
  const [incidentsError, setIncidentsError] = useState(initialIncidentsError);
  const [currentRuntimeStatus, setCurrentRuntimeStatus] = useState(runtimeStatus);
  const [period, setPeriod] = useState("30");

  const periodLabel = useMemo(() => `Last ${period} days`, [period]);

  return (
    <>
      <section className="toolbar-row">
        <label htmlFor="period" className="muted">Period</label>
        <select id="period" className="period-filter" value={period} onChange={(e) => setPeriod(e.target.value)} aria-label="Filter dashboard period">
          <option value="7">Last 7 days</option><option value="30">Last 30 days</option><option value="90">Last 90 days</option>
        </select>
        <button className="upload-btn refresh-btn" onClick={async () => {
          const [a, i] = await Promise.allSettled([getAlerts(), getIncidents()]);
          if (a.status === "fulfilled") { setAlerts(a.value); setAlertsError(undefined); } else setAlertsError(a.reason?.message ?? "Failed");
          if (i.status === "fulfilled") { setIncidents(i.value); setIncidentsError(undefined); } else setIncidentsError(i.reason?.message ?? "Failed");
        }}>Refresh</button>
      </section>
      <StatCards health={health} runtimeStatus={currentRuntimeStatus} alerts={alerts} incidents={incidents} />
      <section className="middle-grid">
        <RiskTrendChart periodLabel={periodLabel} />
        <UploadPanel onDetections={setDetections} onRefreshRuntimeStatus={async () => {
          try {
            const latestRuntime = await getRuntimeStatus();
            setCurrentRuntimeStatus(latestRuntime);
          } catch {
            // leave existing runtime status in place
          }
        }} />
      </section>
      <section className="lower-grid">
        <DataTables detections={detections} incidents={incidents} incidentsError={incidentsError} onRetryIncidents={async () => {
          try { const result = await getIncidents(); setIncidents(result); setIncidentsError(undefined); }
          catch (error) { setIncidentsError(error instanceof Error ? error.message : "Failed to reload"); }
        }} />
        <AlertsList alerts={alerts} error={alertsError} onRetry={async () => {
          try { const result = await getAlerts(); setAlerts(result); setAlertsError(undefined); }
          catch (error) { setAlertsError(error instanceof Error ? error.message : "Failed to reload"); }
        }} />
      </section>
    </>
  );
}
