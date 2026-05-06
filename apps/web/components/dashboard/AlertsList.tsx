const alerts = [
  { title: "Critical CVE exploit attempt", level: "Critical" },
  { title: "Unmanaged endpoint detected", level: "High" },
  { title: "DNS tunneling anomaly", level: "Medium" }
];

export function AlertsList() {
  return (
    <article className="card alerts-card">
      <h3>Active Alerts</h3>
      <ul>
        {alerts.map((alert) => (
          <li key={alert.title}>
            <span>{alert.title}</span>
            <strong>{alert.level}</strong>
          </li>
        ))}
      </ul>
    </article>
  );
}
