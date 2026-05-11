import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export default function PoliciesPage() {
  return (
    <main className="app-shell">
      <Sidebar />
      <section className="content">
        <Topbar />
        <div className="card table-card">
          <div className="panel-head">
            <h2>Policies</h2>
            <span className="badge pri-low">Controlled</span>
          </div>
          <p className="muted">Manage baseline controls, prevention rules, and exception handling policies.</p>
          <p className="muted">Changes should be reviewed before rollout to production environments.</p>
        </div>
      </section>
    </main>
  );
}
