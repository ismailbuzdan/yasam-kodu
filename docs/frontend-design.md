---
tags:
  - memory/architecture
---

# Frontend tasarım ve davranış sistemi

## Görsel dil

Editorial Archive + Modern Mysticism. En fazla 1280 px içerik, geniş kenar boşlukları,
ince arşiv çizgileri, serif başlıklar ve asimetrik bölüm düzenleri kullanılır.
Ana sayfadaki soyut astronomik çizim dekoratiftir; harita veya hesaplama çıktısı değildir.
Tekrarlanan Code Line motifi ORIGIN / PATTERN / INTERPRETATION indekslerini taşır.

`globals.css` renk token'ları: background, surface, surface-light, ink, ink-muted,
bronze, bronze-soft, line, line-strong, danger ve success. Success ilerideki başarılı
işlem geri bildirimleri için ayrılmıştır; sahte hesaplama başarı durumu gösterilmez.

Başlıklarda Cormorant Garamond, gövde ve arayüzde Manrope kullanılır. Dosyalar ve OFL
lisansları `frontend/src/app/fonts` içindedir. Font yönetimi `next/font/local` ile
yapılır; derleme ve kullanıcı ziyareti Google font sunucusuna bağlı değildir.
Fontlar kayıpsız WOFF2 biçiminde toplam yaklaşık 257 KiB sunulur. Özgün TTF dosyaları
referans için korunur. Dönüştürme yereldeki FontTools ile yapıldı; projeye bağımlılık eklenmedi.

Kaynaklar: [Next.js font yönetimi](https://nextjs.org/docs/app/getting-started/fonts),
[Cormorant Garamond](https://github.com/google/fonts/tree/main/ofl/cormorantgaramond),
[Manrope](https://github.com/google/fonts/tree/main/ofl/manrope).

## Form davranışı

- Ad, soyad, doğum tarihi, ülke ve şehir zorunludur. Boşluk içeren boş değerler reddedilir.
- Tarih gerçek bir takvim günü olmalı ve kullanıcının yerel bugününden sonra olmamalıdır.
- Saat isteğe bağlıdır. Girilmişse 24 saatlik HH:mm biçimi doğrulanır.
- Yaklaşık seçimi, isteğe bağlı başlangıç/bitiş saatlerini açar. İkisi de girilirse
  aynı gün içinde başlangıç ≤ bitiş olmalıdır. Gece yarısını aşan aralık desteklenmez.
- Bilmiyorum seçimi saat girişini temizler ve devre dışı bırakır. Kesinlik değişiminde
  gizlenen aralık değerleri ve hataları temizlenir.
- Alan terk edildiğinde ve form gönderildiğinde doğrulama yapılır; hatalı alan
  düzeltilirken hata güncellenir. Gönderimde DOM sırasındaki ilk hataya odaklanılır.
- Geçerli form `/sonuc` taslağına yönlendirir. İsim/tarih/konum query parametresi,
  localStorage, sessionStorage, cookie veya API üzerinden aktarılmaz.
- Ülke ve şehir serbest metindir; konum servisi veya geocoding yoktur.

## Erişilebilirlik

Semantik başlıklar, fieldset/legend grupları, açık zorunluluk etiketleri,
aria-describedby ile yardımcı metin/hata ilişkileri ve aria-invalid kullanılır.
Hata özeti ve koşullu alan değişiklikleri live region ile duyurulur. Odak görünürdür;
mobil menü expanded/controls durumlarını bildirir, Escape ile kapanıp odağı düğmeye verir.
Kontroller en az 44 px dokunma alanına sahiptir. Input metni mobilde 16 px'tir.
Hero animasyonları kısa ve bir defalıktır; prefers-reduced-motion hareketi kapatır.
Ölçülen kontrastlar: ana metin 12.49:1, yardımcı metin 5.26:1, bronz metin 5.11:1,
hata metni 6.10:1; input kenar çizgisi / input zemini 3.25:1.
Gönder düğmesi JavaScript hazır olmadan devre dışıdır; native form gönderimi engellenir.

## Doğrulama

`npm run lint`, `npm run typecheck`, `npm test`, `npm run build`.
Node testleri boş alan, gelecek tarih, gerçek takvim günü, artık yıl, saat biçimi,
yaklaşık aralık ve bilinmeyen saat sınırlarını kapsar.
Tarayıcı kontrolü: dört route; 375, 768, 1024 ve 1440 px; mobil menü;
boş/geçersiz/geçerli gönderim ve ilk hataya odaklanma.
