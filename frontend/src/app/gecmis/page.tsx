import type { Metadata } from "next";
import Link from "next/link";
import { CodeLine } from "@/components/decorative/code-line";
export const metadata: Metadata = { title: "Analiz arşivi" };
export default function HistoryPage() {
  return <div className="archive-page container"><header className="archive-heading"><p className="eyebrow">KİŞİSEL KOLEKSİYON</p><h1>ANALİZ <em>ARŞİVİ</em></h1><CodeLine index="00" label="KAYIT" /></header><section className="empty-archive" aria-labelledby="empty-title"><div className="archive-symbol" aria-hidden="true"><span /><span /><span /></div><p className="micro">İLK SAYFA SENİ BEKLİYOR</p><h2 id="empty-title">Henüz kaydedilmiş bir<br />Yaşam Kodu bulunmuyor.</h2><p>Kişisel okumaların için ayrılmış bir alan.<br />Analizleri kaydetme özelliği ilerleyen aşamada açılacak.</p><Link className="button" href="/analiz">İlk Kodumu Oluştur <span aria-hidden="true">↗</span></Link></section></div>;
}
