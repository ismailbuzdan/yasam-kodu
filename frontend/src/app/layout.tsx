import type { Metadata } from "next";
import localFont from "next/font/local";
import Link from "next/link";
import { Header } from "@/components/layout/header";
import "./globals.css";
const editorial = localFont({ src: "./fonts/CormorantGaramond.woff2", variable: "--font-editorial", display: "swap", weight: "300 700", fallback: ["Georgia"] });
const sans = localFont({ src: "./fonts/Manrope.woff2", variable: "--font-body", display: "swap", weight: "200 800", fallback: ["sans-serif"] });
export const metadata: Metadata = {
  title: { default: "YAŞAM KODU — Kendine bir başlangıç", template: "%s | YAŞAM KODU" },
  description: "Astroloji, numeroloji ve Human Design verilerini tek bir kişisel yaşam profilinde buluşturacak analiz deneyimi.",
};
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="tr" data-scroll-behavior="smooth" className={editorial.variable + " " + sans.variable}><body>
    <a className="skip-link" href="#main">İçeriğe geç</a><Header />
    <main id="main" tabIndex={-1}>{children}</main>
    <footer className="site-footer container">
      <Link className="wordmark" href="/">YAŞAM KODU<span className="wordmark-point" aria-hidden="true" /></Link>
      <p>Her hikâye bir başlangıç anı taşır.</p><span className="micro">KİŞİSEL KEŞİF ARŞİVİ</span>
    </footer>
  </body></html>;
}
