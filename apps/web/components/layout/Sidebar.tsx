"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const nav = [
  { label: "Overview", href: "/" },
  { label: "Threat Feed", href: "/threat-feed" },
  { label: "Incidents", href: "/incidents" },
  { label: "Endpoints", href: "/endpoints" },
  { label: "Policies", href: "/policies" },
  { label: "Integrations", href: "/integrations" },
  { label: "Reports", href: "/reports" }
];

export function Sidebar() {
  const pathname = usePathname();

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
        {nav.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname === item.href || pathname?.startsWith(`${item.href}/`);

          return (
            <Link key={item.href} href={item.href} className={`nav-item ${isActive ? "active" : ""}`}>
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="sidebar-footer">
        <p>v2.6.1</p>
        <p>Cluster: Healthy</p>
      </div>
    </aside>
  );
}
