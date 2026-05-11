import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export default function EndpointsPage() {
  return (
    <main className="app-shell">
      <Sidebar />
      <section className="content">
        <Topbar />
        <div className="card table-card">
          <div className="panel-head">
            <h2>Endpoints</h2>
            <span className="badge">Inventory</span>
          </div>
          <p className="muted">Inspect monitored devices, protection posture, and endpoint coverage status.</p>
          <p className="muted">Detailed host telemetry and actions are available in endpoint modules.</p>
        </div>
      </section>
    </main>
  );
}
