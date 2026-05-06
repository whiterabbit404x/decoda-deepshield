"use client";

import { useState } from "react";

import { AlertsList } from "@/components/dashboard/AlertsList";
import { ChartPanel } from "@/components/dashboard/ChartPanel";
import { DataTables } from "@/components/dashboard/DataTables";
import { StatCards } from "@/components/dashboard/StatCards";
import { UploadPanel } from "@/components/dashboard/UploadPanel";
import { type Alert, type DetectionOutput, type HealthResponse, type Incident } from "@/types/api";

interface DashboardClientProps {
  health: HealthResponse | null;
  alerts: Alert[];
  incidents: Incident[];
  alertsError?: string;
  incidentsError?: string;
}

export function DashboardClient({ health, alerts, incidents, alertsError, incidentsError }: DashboardClientProps) {
  const [detections, setDetections] = useState<DetectionOutput[]>([]);

  return (
    <>
      <StatCards health={health} alerts={alerts} incidents={incidents} />
      <section className="middle-grid">
        <ChartPanel />
        <UploadPanel onDetections={setDetections} />
      </section>
      <section className="lower-grid">
        <DataTables detections={detections} incidents={incidents} incidentsError={incidentsError} />
        <AlertsList alerts={alerts} error={alertsError} />
      </section>
    </>
  );
}
