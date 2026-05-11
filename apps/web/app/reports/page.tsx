import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export default function ReportsPage() {
  return (
    <main className="app-shell">
      <Sidebar />
      <section className="content">
        <Topbar />
        <div className="card table-card">
          <div className="panel-head">
            <h2>Reports</h2>
            <span className="badge">Export Ready</span>
          </div>
          <p className="muted">Generate summaries for operations, compliance, and executive stakeholder updates.</p>
          <p className="muted">Scheduled report templates can be configured from this workspace.</p>
        </div>
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
