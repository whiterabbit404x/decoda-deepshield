const detections = ["PowerShell lateral movement", "Suspicious login geography", "Data exfiltration pattern"];
const incidents = ["INC-2031  Credential stuffing", "INC-2030  Privilege escalation", "INC-2029  Ransomware staging"];

export function DataTables() {
  return (
    <section className="tables-grid">
      <article className="card table-card">
        <h3>Recent Detections</h3>
        <ul>{detections.map((d) => <li key={d}>{d}</li>)}</ul>
      </article>
      <article className="card table-card">
        <h3>Incidents</h3>
        <ul>{incidents.map((i) => <li key={i}>{i}</li>)}</ul>
      </article>
    </section>
  );
}
