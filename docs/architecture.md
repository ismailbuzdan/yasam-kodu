---
tags:
  - memory/architecture
---

# Mimari sınırlar

Frontend, Next.js App Router ve TypeScript strict mode kullanır. Tailwind CSS ve
`src/app/globals.css` içindeki renk/tipografi değişkenleri görsel temeli oluşturur.
Cormorant Garamond ve Manrope, `next/font/local` ile yerelden sunulur.
Fontlar `src/app/fonts` altında OFL lisanslarıyla bulunur; dış font isteği gerekmez.
Header ve doğum formu client component, sayfa içerikleri server component'tir.

Backend bağımsız FastAPI uygulamasıdır. `api` HTTP route'larını, `schemas`
Pydantic yanıt modellerini, `core` ortam yapılandırmasını barındırır. `models` ve
`services` ileride kullanılmak üzere boş Python paketleridir.

Tek endpoint `GET /health`'tir. Otomatik API dokümantasyonu endpoint'leri bu aşamada
kapalıdır. Development CORS yalnızca yerel 3000 portuna GET erişimi sağlar;
production ortamında bu izinler uygulanmaz. CORS bir kimlik doğrulama sistemi değildir.

Form, React state üzerinde giriş ve frontend doğrulaması sağlar. Geçerli form sadece
`/sonuc` taslağına geçer. Veri gönderimi, kalıcı depolama, frontend/backend bağlantısı
veya analiz motoru yoktur. PostgreSQL, Swiss Ephemeris/pyswisseph, OpenAI ve PDF üretimi gelecekte
değerlendirilecektir; bu aşamada bağımlılıkları veya entegrasyonları eklenmemiştir.
