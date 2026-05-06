export function UploadPanel() {
  return (
    <article className="card upload-panel">
      <h2>Upload Intelligence</h2>
      <p className="muted">Drop IOC files or forensic bundles for automated triage.</p>
      <button className="upload-btn">Upload File</button>
      <div className="upload-meta">
        <p>Supported: CSV, JSON, PCAP</p>
        <p>Max size: 4 GB</p>
      </div>
    </article>
  );
}
