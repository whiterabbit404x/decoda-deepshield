export function Topbar() {
  return (
    <header className="topbar card">
      <input
        className="search"
        placeholder="Search detections, indicators, incidents..."
        aria-label="Search"
      />
      <div className="topbar-right">
        <span className="status-pill">System Secure</span>
        <div className="account">
          <div className="avatar">DS</div>
          <div>
            <p className="account-name">Dana Security</p>
            <p className="account-role">Security Director</p>
          </div>
        </div>
      </div>
    </header>
  );
}
