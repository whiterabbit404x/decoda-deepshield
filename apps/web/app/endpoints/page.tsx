import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export default function EndpointsPage() {
  const endpoints = [
    { name: "KYC Upload API", status: "Healthy", badge: "pri-low", seen: "last seen --" },
    { name: "Audio Forensics API", status: "Degraded", badge: "pri-medium", seen: "last seen --" },
    { name: "Video Session API", status: "Healthy", badge: "pri-low", seen: "last seen --" },
    { name: "Webhook Receiver", status: "Pending", badge: "pri-high", seen: "last seen --" },
  ];

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
          <p className="muted">Monitor API endpoint health and availability across your fraud prevention stack.</p>
          <ul>
            {endpoints.map((endpoint) => (
              <li key={endpoint.name}>
                <div className="panel-head">
                  <strong>{endpoint.name}</strong>
                  <span className={`badge ${endpoint.badge}`}>{endpoint.status}</span>
                </div>
                <p className="muted">{endpoint.seen}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  );
}
