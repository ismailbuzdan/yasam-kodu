"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRef, useState } from "react";
export function Header() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const toggle = useRef<HTMLButtonElement>(null);
  function links() {
    return <>
      <Link href="/analiz" aria-current={pathname === "/analiz" ? "page" : undefined} onClick={() => setOpen(false)}>Analiz</Link>
      <Link href="/yaklasim" aria-current={pathname === "/yaklasim" ? "page" : undefined} onClick={() => setOpen(false)}>Yaklaşım</Link>
      <Link href="/gecmis" aria-current={pathname === "/gecmis" ? "page" : undefined} onClick={() => setOpen(false)}>Geçmiş</Link>
      <Link href="/analiz" className="button button-small" onClick={() => setOpen(false)}>Kodumu Keşfet <span aria-hidden="true">↗</span></Link>
    </>;
  }
  return <header className="site-header" onKeyDown={(event) => {
    if (event.key === "Escape" && open) { setOpen(false); toggle.current?.focus(); }
  }} onBlur={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false); }}>
    <div className="header-inner container">
      <Link href="/" className="wordmark" aria-label="Yaşam Kodu ana sayfa" onClick={() => setOpen(false)}>YAŞAM KODU<span className="wordmark-point" aria-hidden="true" /></Link>
      <nav className="desktop-nav" aria-label="Ana gezinme">{links()}</nav>
      <button ref={toggle} type="button" className="menu-toggle" aria-expanded={open} aria-controls="mobile-nav" onClick={() => setOpen(!open)}>{open ? "Kapat" : "Menü"}<span aria-hidden="true">{open ? "−" : "+"}</span></button>
    </div>
    <nav id="mobile-nav" className="mobile-nav container" aria-label="Mobil gezinme" hidden={!open}>{links()}</nav>
  </header>;
}
