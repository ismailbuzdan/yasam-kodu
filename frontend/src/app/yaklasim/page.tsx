import type { Metadata } from "next";
import Link from "next/link";
import { CodeLine } from "@/components/decorative/code-line";

export const metadata: Metadata = {
  title: "Yaklaşım",
  description: "Yaşam Kodu'nun astroloji, numeroloji ve Human Design sistemlerini neden ve nasıl birlikte ele aldığını keşfedin.",
};

const systems = [
  {
    index: "01 / ORIGIN",
    title: "ASTROLOJİ",
    definition: "Astroloji, kişinin doğum tarihi, doğum saati ve doğum yerinden hareketle doğum anındaki gök cisimlerinin konumlarını sembolik olarak yorumlayan geleneksel bir sistemdir.",
    signals: ["Güneş", "Ay", "Yükselen", "Gezegenler", "Evler", "Açılar", "Ay düğümleri", "MC ve temel noktalar"],
    questions: ["Temel karakter eğilimleri", "Duygusal yapı", "İlişki dinamikleri", "Kariyer temaları", "Hayat alanlarındaki sembolik örüntüler", "Dönemsel astrolojik döngüler"],
    reason: "Doğum anına bağlı en ayrıntılı sembolik veri katmanını oluşturduğu için kullanılır. Doğum saati özellikle yükselen, evler ve bazı diğer hesaplamalarda belirleyicidir.",
  },
  {
    index: "02 / PATTERN",
    title: "NUMEROLOJİ",
    definition: "Numeroloji, isim ve doğum tarihinden türetilen sayı örüntülerine sembolik anlamlar yükleyen bir yorum sistemidir.",
    signals: ["Yaşam Yolu Sayısı", "Doğum Günü Sayısı", "İfade / Kader Sayısı", "Ruh Arzusu", "Kişilik Sayısı", "Olgunluk Sayısı", "Kişisel Yıl"],
    questions: ["Tekrar eden temalar", "Kişisel yönelimler", "İç motivasyon", "Dışarıya yansıyan ifade", "Dönemsel sayı döngüleri"],
    reason: "Astrolojiden tamamen farklı bir hesaplama yöntemiyle ikinci bir sembolik perspektif sağlar. Aynı tema farklı sistemlerde tekrar ediyorsa, bunu ileride karşılaştırabilmek için kullanılır.",
  },
  {
    index: "03 / INTERPRETATION",
    title: "HUMAN DESIGN",
    definition: "Human Design; astroloji, I Ching'in 64 hexagram yapısı ve kendine özgü BodyGraph sisteminden yararlanan modern bir kişisel farkındalık sistemidir.",
    signals: ["Type", "Strategy", "Authority", "Profile", "Centers", "Gates", "Channels", "Definition", "Signature", "Not-Self Theme", "Incarnation Cross"],
    questions: ["Karar verme yaklaşımı", "Enerji kullanımı", "Çevreyle etkileşim", "Açık ve tanımlı merkezlerin sembolik anlamları"],
    reason: "Astroloji ve numerolojiden farklı olarak özellikle karar verme ve enerji dinamikleri üzerine ek bir yorum katmanı sunduğu için kullanılır. Bilimsel olarak doğrulanmış bir psikolojik ölçüm yöntemi değildir.",
  },
] as const;

function SystemSection({ system }: { system: (typeof systems)[number] }) {
  return <section className="approach-system container" aria-labelledby={`${system.title}-title`}>
    <div className="approach-system-index"><p className="eyebrow">{system.index}</p><CodeLine index={system.index.slice(0, 2)} label={system.index.split(" / ")[1]} /></div>
    <div className="approach-system-content">
      <h2 id={`${system.title}-title`}>{system.title}</h2>
      <div className="approach-system-grid">
        <div><h3>Nedir?</h3><p>{system.definition}</p></div>
        <div><h3>Yaşam Kodu&apos;nda</h3><ul className="signal-list">{system.signals.map((signal) => <li key={signal}>{signal}</li>)}</ul></div>
        <div><h3>Neyi anlamaya çalışır?</h3><ul>{system.questions.map((question) => <li key={question}>{question}</li>)}</ul></div>
        <div className="approach-reason"><h3>Neden kullanılıyor?</h3><p>{system.reason}</p></div>
      </div>
    </div>
  </section>;
}

export default function ApproachPage() {
  return <>
    <section className="approach-hero container" aria-labelledby="approach-title">
      <div className="approach-hero-label micro"><span>YAKLAŞIM / 00</span><span>YAŞAM KODU</span></div>
      <div className="approach-hero-copy"><h1 id="approach-title">Üç sistem.<br /><em>Tek kişisel profil.</em></h1><p>Yaşam Kodu; astroloji, numeroloji ve Human Design&apos;ı birbirinin yerine geçen sistemler olarak değil, aynı kişiye farklı açılardan bakan üç ayrı sembolik çerçeve olarak ele alır.</p></div>
      <div className="approach-code-words" aria-hidden="true"><span>ORIGIN</span><i /><span>PATTERN</span><i /><span>INTERPRETATION</span></div>
    </section>

    <div className="approach-systems">{systems.map((system) => <SystemSection key={system.title} system={system} />)}</div>

    <section className="comparison-section" aria-labelledby="comparison-title"><div className="container">
      <p className="eyebrow">KARŞILAŞTIRMA ALANI / 04</p><h2 id="comparison-title">Üç ayrı dil.<br /><em>Tek bir karşılaştırma alanı.</em></h2>
      <p className="comparison-intro">Yaşam Kodu&apos;nun amacı üç sistemi zorla aynı sonuca ulaştırmak değildir. Aynı temaların nerelerde tekrarlandığını, nerelerde ayrıldığını ve farklı sistemlerin aynı kişiye nasıl farklı perspektiflerden baktığını görünür hale getirir.</p>
      <div className="comparison-map" aria-hidden="true"><div><span>ASTROLOJİ</span><p>Doğum anı / gökyüzü yapısı</p></div><div><span>NUMEROLOJİ</span><p>İsim / tarih / sayı örüntüleri</p></div><div><span>HUMAN DESIGN</span><p>Enerji / karar / BodyGraph</p></div><div className="comparison-result"><span>↓</span><strong>YAŞAM KODU</strong></div></div>
    </div></section>

    <section className="calculation-section container" aria-labelledby="calculation-title"><div className="calculation-number" aria-hidden="true">05</div><div><p className="eyebrow">SİSTEM MİMARİSİ</p><h2 id="calculation-title">Hesaplanan veri.<br /><em>Yorumlanan anlam.</em></h2></div><div className="calculation-copy"><p>Yaşam Kodu&apos;nun gelecekteki hesaplama motorlarında astrolojik konumlar, numeroloji sayıları ve Human Design bileşenleri yapay zekâ tarafından tahmin edilmeyecek. Önce deterministik hesaplama motorları tarafından üretilecek.</p><p>Yapay zekâ kullanılırsa, yalnızca doğrulanmış sonuçların yorumlanması ve sistemler arasındaki ilişkilerin anlaşılır biçimde anlatılması için kullanılacak. Bu, gelecekteki sistem mimarisine dair bir yaklaşımdır; uygulamada henüz bir AI entegrasyonu bulunmuyor.</p></div></section>

    <section className="limits-section" aria-labelledby="limits-title"><div className="container limits-layout"><div><p className="eyebrow">DİPNOT / 06</p><h2 id="limits-title">Bu analiz<br /><em>ne değildir?</em></h2></div><div><p>Yaşam Kodu; tıbbi değerlendirme, psikolojik tanı aracı veya bilimsel kişilik testi değildir. Geleceği kesin olarak öngördüğünü iddia etmez; önemli sağlık, finans, hukuk ya da yaşam kararlarının tek dayanağı olmamalıdır.</p><p>Astroloji, numeroloji ve Human Design bilimsel olarak doğrulanmış kişilik ölçüm sistemleri değildir. Yaşam Kodu bunları kişisel farkındalık, öz değerlendirme ve eğlence amaçlı sembolik yorumlar olarak sunar.</p></div></div></section>

    <section className="approach-closing container" aria-labelledby="approach-closing-title"><p className="eyebrow">BAŞLANGIÇ NOKTAN</p><h2 id="approach-closing-title">Kendi kodunu<br /><em>keşfet.</em></h2><p>Doğum bilgilerinle kişisel profilinin ilk satırını oluştur.</p><Link className="button" href="/analiz">Analizimi Başlat <span aria-hidden="true">↗</span></Link></section>
  </>;
}
