const nav = ["Overview", "Threat Feed", "Incidents", "Endpoints", "Policies", "Integrations", "Reports"];

export function Sidebar() {
  return (
    <aside className="sidebar" aria-label="Primary navigation">
      <div className="brand">
        <span className="brand-glow" />
        <div>
          <p className="brand-title">DeepShield</p>
          <p className="brand-subtitle">Enterprise SOC</p>
        </div>
      </div>
      <nav className="nav-list" aria-label="Security sections">
        {nav.map((item, i) => (
          <button key={item} className={`nav-item ${i === 0 ? "active" : ""}`}>
            {item}
          </button>
        ))}
      </nav>
      <div className="sidebar-footer">
        <p>v2.6.1</p>
        <p>Cluster: Healthy</p>
      </div>
    </aside>
  );
}
