import { AlertsList } from "@/components/dashboard/AlertsList";
import { ChartPanel } from "@/components/dashboard/ChartPanel";
import { DataTables } from "@/components/dashboard/DataTables";
import { StatCards } from "@/components/dashboard/StatCards";
import { UploadPanel } from "@/components/dashboard/UploadPanel";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export default function HomePage() {
  return (
    <main className="app-shell">
      <Sidebar />
      <section className="content">
        <Topbar />
        <StatCards />
        <section className="middle-grid">
          <ChartPanel />
          <UploadPanel />
        </section>
        <section className="lower-grid">
          <DataTables />
          <AlertsList />
        </section>
        <footer className="footer card">
          <div className="footer-links">
            <a href="#">Documentation</a>
            <a href="#">API</a>
            <a href="#">Trust Center</a>
            <a href="#">Support</a>
          </div>
          <p>© 2026 DeepShield Systems · Privacy · Terms · Compliance</p>
        </footer>
      </section>
    </main>
  );
}
