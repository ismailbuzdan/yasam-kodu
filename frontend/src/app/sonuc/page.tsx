import type { Metadata } from "next";
import Link from "next/link";
import { CodeLine } from "@/components/decorative/code-line";
import { BirthProfileSummary } from "@/components/report/birth-profile-summary";
export const metadata: Metadata = { title: "Kişisel analiz taslağı" };
const chapters = ["Karakter", "Duygusal Yapı", "Aşk & İlişkiler", "Kariyer & Para", "Hayat Temaları", "Numeroloji", "Human Design", "Gölge Yönler", "Zaman Çizgisi", "Genel Özet"];
export default function ResultPage() {
  return <div className="report-page container">
    <header className="report-heading"><p className="eyebrow">YAŞAM KODU <span>/ RAPOR TASLAĞI</span></p><h1>Kişisel <em>Analiz</em></h1><p>Hikâyenin satırları burada bir araya gelecek.</p></header>
    <BirthProfileSummary />
    <dl className="report-markers">{["Güneş", "Ay", "Yükselen"].map(label => <div key={label}><dt>{label}</dt><dd><span aria-hidden="true">—</span><span className="sr-only">Henüz hesaplanmadı</span></dd></div>)}</dl>
    <div className="report-layout"><section className="report-index" aria-labelledby="index-title"><p className="eyebrow">RAPORUN İÇİNDEN</p><h2 id="index-title">İçerik indeksi</h2><ol>{chapters.map((chapter, index) => <li key={chapter}><span className="micro" aria-hidden="true">{String(index + 1).padStart(2, "0")}</span><span>{chapter}</span></li>)}</ol></section>
      <section className="report-preview" aria-labelledby="preview-title"><CodeLine index="03" label="INTERPRETATION" /><div className="placeholder-monogram" aria-hidden="true">YK</div><p className="eyebrow">HENÜZ HESAPLANMADI</p><h2 id="preview-title">Bir sonraki<br /><em>sayfa hazırlanıyor.</em></h2><p>Hesaplama motorları sonraki aşamada bağlanacak.</p><p className="report-note">Bu ekran raporun tasarım taslağıdır. Girilen bilgiler bu aşamada yalnızca doğrulandı; kişisel analiz üretilmedi.</p><div className="skeleton-lines" aria-hidden="true"><span /><span /><span /></div><Link className="text-link" href="/analiz">Bilgi girişine dön <span aria-hidden="true">↗</span></Link></section>
    </div>
  </div>;
}
