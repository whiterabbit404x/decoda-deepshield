import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export default function ReportsPage() {
  const reports = [
    "Synthetic Media Risk Report",
    "Incident Summary",
    "Audit Trail Export",
    "Compliance Evidence Package",
  ];

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
          <p className="muted">Generate downloadable exports for operations, risk, and compliance teams.</p>
          <ul>
            {reports.map((report) => (
              <li key={report}>
                <div className="panel-head">
                  <strong>{report}</strong>
                  <button type="button" className="badge pri-low">
                    Export
                  </button>
                </div>
              </li>
            ))}
          </ul>
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
