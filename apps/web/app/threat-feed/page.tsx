import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export default function ThreatFeedPage() {
  const detections = [
    { signal: "Voice clone attempt", severity: "pri-high", when: "2m ago" },
    { signal: "Replay attack fingerprint", severity: "pri-medium", when: "11m ago" },
    { signal: "Suspicious session velocity", severity: "pri-low", when: "26m ago" },
  ];

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
          <p className="muted">Recent detections and threat signals across onboarding and transaction sessions.</p>
          <ul>
            {detections.map((item) => (
              <li key={item.signal}>
                <div className="panel-head">
                  <strong>{item.signal}</strong>
                  <span className={`badge ${item.severity}`}>{item.when}</span>
                </div>
                <p className="muted">Actionable signal observed by DeepShield detectors.</p>
              </li>
            ))}
          </ul>
          <p className="state-text">
            No additional alerts right now. We will surface synthetic media, KYC bypass, voice clone, replay attack,
            and suspicious session events here as new evidence arrives.
          </p>
        </div>
      </section>
    </main>
  );
}
