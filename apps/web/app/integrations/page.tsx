import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export default function IntegrationsPage() {
  const integrations = [
    { name: "KYC Provider", action: "Configure", style: "pri-low" },
    { name: "Bank Fraud Queue", action: "Configure", style: "pri-low" },
    { name: "Case Management", action: "Configure", style: "pri-low" },
    { name: "Webhook", action: "Configure", style: "pri-low" },
    { name: "Object Storage", action: "Coming soon", style: "pri-medium" },
  ];

  return (
    <main className="app-shell">
      <Sidebar />
      <section className="content">
        <Topbar />
        <div className="card table-card">
          <div className="panel-head">
            <h2>Integrations</h2>
            <span className="badge">Connected Apps</span>
          </div>
          <p className="muted">Connect your ecosystem to orchestrate fraud decisions and case routing.</p>
          <ul>
            {integrations.map((integration) => (
              <li key={integration.name}>
                <div className="panel-head">
                  <strong>{integration.name}</strong>
                  <button type="button" className={`badge ${integration.style}`}>
                    {integration.action}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  );
}
