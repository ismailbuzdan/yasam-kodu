# Yaşam Kodu — Codex Instructions

Her geliştirme görevinden önce sırasıyla `docs/00_START_HERE.md`,
`docs/04_CURRENT_STATE.md`, `docs/03_ROADMAP.md` ve görevle ilgili teknik belgeyi oku.

- Frontend: Next.js, TypeScript strict, App Router, Tailwind CSS.
- Backend: FastAPI, Python, Pydantic.
- Calculation layer deterministik olmalıdır. Interpretation layer yalnız doğrulanmış hesap sonuçlarını yorumlar.
- AI; astrolojik konum, numeroloji sayısı veya Human Design BodyGraph verisi hesaplamaz.
- Mevcut davranışı gereksiz değiştirme, kapsam dışı özellik ekleme ve kabul edilmiş kararları bozma.
- Proje lisansı AGPL-3.0'dır: AGPL-3.0 ile uyumsuz dependency ekleme, her yeni dependency için lisans uyumluluğunu kontrol et ve lisans kararını değiştirme.
- Docker Compose, kullanılabildiğinde tekrarlanabilir yerel doğrulama için tercih edilen yöntemdir. Docker daemon erişilemiyorsa doğrudan test komutları kullanılabilir; çalıştırılmamış Docker doğrulamasını başarılı diye raporlama.

Never add real-user birth date/time/location data to tracked fixtures. Use synthetic cases only.

Her görev sonunda ilgili testleri çalıştır; `docs/04_CURRENT_STATE.md` güncelle;
teknik karar oluştuysa `docs/05_DECISIONS.md`, değişiklik kayda değerse `docs/CHANGELOG.md` güncelle.

Backend değişikliklerinde `pytest` ve `pip check` çalıştır. Frontend değiştiyse `npm run lint`,
`npm run typecheck`, `npm test` ve `npm run build` çalıştır. Belirsiz mimari kararlarda uydurma yapma.
