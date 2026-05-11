import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export default function ThreatFeedPage() {
  return (
    <main className="app-shell">
      <Sidebar />
      <section className="content">
        <Topbar />
        <div className="card table-card">
          <div className="panel-head">
            <h2>Threat Feed</h2>
            <span className="badge pri-high">Live</span>
          </div>
          <p className="muted">Track curated indicators and active threat campaigns relevant to your environment.</p>
          <ul>
            <li>
              <span className="muted">Latest intel sync</span>
              <strong>Available in feed API</strong>
            </li>
            <li>
              <span className="muted">Priority focus</span>
              <strong>Ransomware infrastructure</strong>
            </li>
          </ul>
        </div>
      </section>
    </main>
  );
}
