const stats = [
  { label: "Threats Blocked", value: "12,849", delta: "+12.4%" },
  { label: "Active Incidents", value: "17", delta: "-8.1%" },
  { label: "Risk Score", value: "34 / 100", delta: "-3.2%" },
  { label: "Endpoints Online", value: "2,431", delta: "+1.6%" }
];

export function StatCards() {
  return (
    <section className="stats-grid">
      {stats.map((stat) => (
        <article key={stat.label} className="card stat-card">
          <p className="muted">{stat.label}</p>
          <h3>{stat.value}</h3>
          <p className="delta">{stat.delta}</p>
        </article>
      ))}
    </section>
  );
}
