import type { ReactNode } from "react";
import { NavBar } from "./NavBar";
import "./layout.css";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <>
      <NavBar />
      <main>{children}</main>
      <p className="footer-note">
        HMT is a disaster information analysis and misinformation tracking system -- a BE capstone research
        prototype, not a live monitoring service or an emergency-response system.
      </p>
    </>
  );
}

export function PageHeader({ title, subtitle }: { title: string; subtitle?: ReactNode }) {
  return (
    <div className="page-header">
      <h1 className="page-title">{title}</h1>
      {subtitle && <p className="page-subtitle">{subtitle}</p>}
    </div>
  );
}
