export function ChartPanel() {
  return (
    <article className="card chart-panel">
      <div className="panel-head">
        <h2>Risk Trend</h2>
        <span className="muted">Last 30 days</span>
      </div>
      <div className="chart-placeholder" aria-hidden>
        <span />
      </div>
    </article>
  );
}
