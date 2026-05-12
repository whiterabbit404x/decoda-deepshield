import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export default function PoliciesPage() {
  const policies = [
    "Require step-up verification",
    "Hold transaction",
    "Escalate to fraud team",
    "Reject high-risk KYC session",
  ];

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
          <p className="muted">Visual policy controls for incident response actions. No settings are persisted yet.</p>
          <ul>
            {policies.map((policy) => (
              <li key={policy}>
                <div className="panel-head">
                  <strong>{policy}</strong>
                  <button type="button" className="badge pri-low" aria-pressed="false">
                    Off
                  </button>
                </div>
                <p className="muted">Toggle preview only</p>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  );
}
