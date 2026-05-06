import { DashboardClient } from "@/components/dashboard/DashboardClient";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { getAlerts, getHealth, getIncidents } from "@/lib/api";

export default async function HomePage() {
  const [healthResult, alertsResult, incidentsResult] = await Promise.allSettled([
    getHealth(),
    getAlerts(),
    getIncidents()
  ]);

  const health = healthResult.status === "fulfilled" ? healthResult.value : null;
  const alerts = alertsResult.status === "fulfilled" ? alertsResult.value : [];
  const incidents = incidentsResult.status === "fulfilled" ? incidentsResult.value : [];

  return (
    <main className="app-shell">
      <Sidebar />
      <section className="content">
        <Topbar />
        <DashboardClient
          health={health}
          alerts={alerts}
          incidents={incidents}
          alertsError={alertsResult.status === "rejected" ? alertsResult.reason?.message : undefined}
          incidentsError={incidentsResult.status === "rejected" ? incidentsResult.reason?.message : undefined}
        />
        <footer className="footer card">
          <div className="footer-links">
            <a href="#">Documentation</a>
            <a href="#">API</a>
            <a href="#">Trust Center</a>
            <a href="#">Support</a>
          </div>
          <p>© 2026 DeepShield Systems · Privacy · Terms · Compliance</p>
        </footer>
      </section>
    </main>
  );
}
