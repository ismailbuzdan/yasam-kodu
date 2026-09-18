import type { Metadata } from "next";
import { BirthProfileForm } from "@/components/form/birth-profile-form";
import { CodeLine } from "@/components/decorative/code-line";
export const metadata: Metadata = { title: "Başlangıç noktan" };
export default function AnalysisPage() {
  return <div className="analysis-page container">
    <header className="page-heading"><p className="eyebrow">KİŞİSEL PROFİL / 01</p><h1>Başlangıç noktanı<br /><em>oluşturalım.</em></h1></header>
    <div className="analysis-layout">
      <aside className="analysis-aside"><CodeLine index="01" label="ORIGIN" /><p className="aside-display">Bir isim.<br />Bir zaman.<br />Bir yer.</p><p>Sana ait bir okumanın ilk satırları, doğduğun anın bilgileriyle başlar.</p><div className="aside-footnote"><span className="micro">BAŞLANGIÇ NOTU</span><p>Saatini bilmiyorsan sorun değil. Bildiğin bilgilerle devam edebilirsin.</p></div></aside>
      <BirthProfileForm />
    </div>
  </div>;
}
