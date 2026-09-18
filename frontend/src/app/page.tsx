import Link from "next/link";
import { CodeLine } from "@/components/decorative/code-line";
const steps = [
  { no: "01", label: "DOĞUM VERİSİ", text: "Doğum tarihi, saat ve konum bilgileri alınır.", en: "ORIGIN" },
  { no: "02", label: "HESAPLAMA", text: "Astroloji, numeroloji ve Human Design sistemleri ayrı ayrı hesaplanır.", en: "PATTERN" },
  { no: "03", label: "YORUM", text: "Sonuçlar tek bir kişisel Yaşam Kodu raporunda birleştirilir.", en: "INTERPRETATION" },
];
const systems = [
  { no: "I", name: "Astroloji", note: "ANIN GÖKYÜZÜ", text: "Doğduğun andaki göksel konumlar üzerinden kişisel haritanın sembolik dilini inceler." },
  { no: "II", name: "Numeroloji", note: "SAYILARIN ÖRÜNTÜSÜ", text: "Adın ve doğum tarihindeki sayısal örüntüler üzerinden farklı bir okuma sunar." },
  { no: "III", name: "Human Design", note: "KİŞİSEL İŞLEYİŞ", text: "Doğum verilerinden hareketle karar alma ve etkileşim biçimlerini kendi sistemi içinde ele alır." },
];
export default function HomePage() {
  return <>
    <section className="hero container" aria-labelledby="hero-title">
      <div className="hero-top micro"><span>KİŞİSEL ANALİZ SİSTEMİ</span><span className="hero-edition">BAŞLANGIÇ / CİLT 01</span></div>
      <div className="hero-grid"><div className="hero-content">
        <h1 id="hero-title">Doğduğun an,<br />bir veri noktası<br /><em>değil.</em></h1>
        <p className="hero-copy">Astroloji, numeroloji ve Human Design verilerini tek bir kişisel yaşam profiline dönüştüren analiz deneyimi.</p>
        <div className="hero-actions"><Link className="button" href="/analiz">Kodumu Keşfet <span aria-hidden="true">↗</span></Link><a className="text-link" href="#nasil-calisir">Nasıl Çalışır? <span aria-hidden="true">↓</span></a></div>
      </div><div className="origin-figure" aria-hidden="true">
        <div className="figure-caption micro"><span>ŞEKİL 01</span><span>BAŞLANGIÇ NOKTASI</span></div>
        <svg viewBox="0 0 440 440" fill="none" className="origin-drawing">
          <circle cx="220" cy="220" r="168" /><circle cx="220" cy="220" r="155" className="drawing-faint" /><circle cx="220" cy="220" r="112" />
          <ellipse cx="220" cy="220" rx="65" ry="168" transform="rotate(32 220 220)" /><ellipse cx="220" cy="220" rx="168" ry="59" transform="rotate(-24 220 220)" />
          <path d="M220 22V418M22 220H418M80 360L360 80" className="drawing-faint" />
          <path d="M215 36H225M215 404H225M36 215V225M404 215V225M212 220H228M220 212V228" />
          <circle cx="220" cy="220" r="4" className="drawing-dot" /><circle cx="326" cy="90" r="5" className="drawing-dot" /><path d="M330 87L366 54H412" />
        </svg>
        <div className="figure-foot"><span className="micro">T₀ / ORIGIN</span><p>Her şey bir an ile başlar.</p></div>
      </div></div><CodeLine index="01" label="ORIGIN — KENDİNE BİR BAŞLANGIÇ" />
    </section>
    <section id="nasil-calisir" className="process-section container" aria-labelledby="process-title">
      <div className="section-heading"><p className="eyebrow">NASIL ÇALIŞIR?</p><h2 id="process-title">Bir an. Üç adım.<br /><em>Bütün bir bakış.</em></h2><p className="section-note">Tasarladığımız yolculuk: doğum verilerinden kişisel bir okuma deneyimine. Hesaplama ve raporlama sonraki aşamada açılacak.</p></div>
      <ol className="process-grid">{steps.map(step => <li key={step.no}><div className="step-heading"><span className="step-number">{step.no}</span><span className="micro">{step.en}</span></div><h3>{step.label}</h3><p>{step.text}</p></li>)}</ol>
    </section>
    <section className="systems-section" aria-labelledby="systems-title"><div className="container systems-layout">
      <div className="systems-intro"><p className="eyebrow">ÜÇ SİSTEM / TEK PROFİL</p><h2 id="systems-title">Farklı diller.<br /><em>Aynı hikâye.</em></h2><p>Her sistem kendi yöntemiyle, birbirinden bağımsız hesaplanacak. Bu okumalar ileride tek bir kişisel raporda bir araya gelecek.</p><Link className="text-link systems-link" href="/yaklasim">Yaklaşımımızı keşfet <span aria-hidden="true">↗</span></Link><CodeLine index="02" label="PATTERN" /></div>
      <div className="system-list">{systems.map(system => <article className="system-row" key={system.no}><span className="system-index">{system.no}</span><div><p className="micro">{system.note}</p><h3>{system.name}</h3><p>{system.text}</p></div></article>)}</div>
    </div></section>
    <section className="closing-section container"><p className="eyebrow">SENİN BAŞLANGIÇ NOKTAN</p><h2>Hikâyene yakından bak.</h2><Link className="button" href="/analiz">Kodumu Keşfet <span aria-hidden="true">↗</span></Link></section>
  </>;
}
