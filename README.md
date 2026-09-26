# YAŞAM KODU

Yaşam Kodu; doğum verisinden Astroloji, Numeroloji ve Human Design hesaplarını tek bir
deterministik Unified Life Code sonucunda birleştiren web uygulamasıdır. Sistem sembolik
öz-farkındalık ve eğlence amaçlıdır; tıbbi, psikolojik, hukuki veya finansal karar aracı değildir.

Mevcut deterministic backend; Birth Profile doğrulama, backend aracılı geocoding, tarihsel timezone,
Astrology, Numerology, Human Design ve Unified Life Code içerir. Kamerî Kod, Unified Life Code v1'den
ayrı bounded bir track'tir: mekanik API'si ve dört-claim'li limited knowledge layer'ı vardır.
Calculation != Interpretation: hesaplar deterministik motorlardan gelir; Stage 11 AI interpretation
henüz başlamamıştır. Otomatik kişisel Esmâ, doğrulanmamış menzil yorumları ve kaynaklandırılmamış dini
yorumlar mevcut değildir.

Henüz mevcut olmayanlar: AI interpretation, final web/PDF report generation, PostgreSQL,
authentication, payments ve production deployment.

## Mevcut hesap endpoint'leri

- `POST /api/v1/astrology/calculate` — resolved UTC ve koordinatlardan deterministik tropikal astroloji.
- `POST /api/v1/numerology/calculate` — Pythagorean numeroloji.
- `POST /api/v1/human-design/calculate` — UTC girdisinden mekanik Human Design sonucu.
- `POST /api/v1/life-code/calculate` — Astrology, Numerology ve Human Design'ın birleşik sonucu.
- `POST /api/v1/kameri/calculate` — ayrı Kamerî mekanik sonuç; `interpretation_present` her zaman `false`.

Endpoint alanları ve hata sınırları için [API Contracts](docs/06_API_CONTRACTS.md), hesap/provenance
sınırları için [Current State](docs/04_CURRENT_STATE.md) ve ilgili teknik belgeler kaynak alınmalıdır.

## Project Memory

Developers and AI agents should begin with [AGENTS.md](AGENTS.md),
[docs/00_START_HERE.md](docs/00_START_HERE.md) and
[docs/04_CURRENT_STATE.md](docs/04_CURRENT_STATE.md). Obsidian users can open `docs/` as a Vault.

## License

Yaşam Kodu is licensed under the GNU Affero General Public License v3.0. See [LICENSE](LICENSE).

## Mimari

```text
yasam-kodu/
├── frontend/             Next.js, TypeScript strict, App Router, Tailwind CSS
│   ├── src/app/          /, /analiz, /yaklasim, /sonuc, /gecmis
│   ├── src/components/  Header, form ve Code Line bileşenleri
│   ├── src/lib/         Form doğrulaması ve merkezi API istemcisi
│   ├── tests/           Doğrulama sınır testleri
│   ├── .env.example
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py       Uygulama fabrikası ve development CORS
│   │   ├── api/          Health, profile/location/timezone ve hesap endpoint'leri
│   │   ├── core/         Ortam ayarları
│   │   ├── models/       Gelecek kullanım için boş paket
│   │   ├── schemas/      Pydantic doğum profili ve yanıt şemaları
│   │   ├── services/     Geocoding, timezone ve deterministik hesap motorları
│   │   └── knowledge/    Kamerî için bounded, kaynaklı knowledge snapshot
│   ├── tests/
│   ├── .env.example
│   ├── requirements.txt
│   └── requirements-dev.txt
├── docs/architecture.md
├── .gitignore
└── README.md
```

İki uygulama bağımsız kurulur ve çalışır. `/analiz` formu yerel doğrulamanın ardından
backend'deki doğum profili doğrulama endpoint'ine istek gönderir. Başarılı, normalize edilmiş profil
yalnızca tarayıcı oturumundaki `sessionStorage` alanında tutulur ve `/sonuc` ekranında gösterilir;
kişisel bilgiler URL'ye eklenmez. Kalıcı veri saklama yoktur. Hesap API'leri backend'de mevcuttur;
AI yorum ve final rapor arayüzü henüz mevcut değildir.

## Development kurulumu

Docker Compose, yeni bilgisayarlarda tercih edilen geliştirme yöntemidir. Host Python veya Node
kurulumu gerekmez. Gerekenler: Git, Docker Desktop (Windows/macOS) veya Docker Engine (Linux) ve
Docker Compose v2.

```powershell
git clone https://github.com/ismailbuzdan/yasam-kodu.git
cd yasam-kodu
docker compose up --build
```

Frontend: [http://localhost:3000](http://localhost:3000).
Backend health: [http://localhost:8000/health](http://localhost:8000/health).

Compose, backend'i Python 3.11 ve frontend'i Node 22 ile çalıştırır. Backend kaynak kodu doğrudan
bind mount edilir; FastAPI `--reload` kullanır. Frontend kaynak kodu da bind mount edilir; Linux
`node_modules` ve `.next` named volume'larda tutulur, böylece host bağımlılıklarıyla karışmaz.
Frontend watcher, Docker/Windows bind mount'larında güvenilir yenileme için polling ile Webpack
development server kullanır.
Tarayıcıdaki `NEXT_PUBLIC_API_BASE_URL` kasıtlı olarak `http://localhost:8000` kalır; Docker servis
adı browser tarafından çözülemez. Development ayarları tracked `.env.example` dosyalarından gelir;
gerçek `.env` ve `.env.local` image içine kopyalanmaz.

### Docker komutları

```powershell
# Ön planda başlat
docker compose up --build

# Arka planda başlat
docker compose up -d --build

# Log ve durum
docker compose logs -f
docker compose ps

# Durdur
docker compose down

# Dependency volume'larını da sıfırla
docker compose down -v
```

`docker compose down -v` bugün yalnız frontend dependency/build volume'larını siler. İleride
PostgreSQL gibi kalıcı veri volume'ları eklenirse bu komut veri silebilir.

Container içi kontroller:

```powershell
docker compose run --rm backend python -m pytest -q
docker compose run --rm backend python -m pip check
docker compose run --rm frontend npm run lint
docker compose run --rm frontend npm run typecheck
docker compose run --rm frontend npm test
docker compose run --rm frontend npm run build
```

Windows'ta OneDrive ile senkronize edilen bind mount'lar file lock, watcher veya performans sorunu
oluşturabilir. Sorun yaşanırsa proje için `C:\Projects\yasam-kodu` gibi OneDrive dışı bir konum
önerilir; bu zorunlu değildir.

### Alternative local development

Docker kullanılamadığında aşağıdaki host kurulumu desteklenir. Stage 6 astroloji backend'i için
Windows'ta Python 3.11 önerilir; sabitlenen pyswisseph sürümünün Python 3.12 kurulumu C++ derleyicisi
gerektirir. Kurulum, hesaplama sözleşmesi ve sınırlamalar:
[Deterministic Astrology](docs/astrology.md). Endpoint: `POST /api/v1/astrology/calculate`.

Ön koşullar: Node.js 22+ (LTS önerilir), npm ve Python 3.11+.
Aşağıdaki komutları `yasam-kodu` klasöründen, iki ayrı terminalde çalıştırın.

### Frontend — terminal 1

```powershell
cd frontend
npm ci
Copy-Item .env.example .env.local
npm run dev
```

Adres: [http://localhost:3000](http://localhost:3000).

### Backend — terminal 2 (Windows PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Sanal ortamı aktive etmek gerekmez. macOS/Linux üzerinde eşdeğeri:

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
cp .env.example .env
.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend ortam dosyasını kopyalamak için macOS/Linux'ta `cp .env.example .env.local` kullanın.

Backend: [http://localhost:8000/health](http://localhost:8000/health).
Kök `/` adresinin 404 dönmesi beklenir. Kullanılabilir endpoint'ler:

```json
{"status":"ok","service":"yasam-kodu-api"}
```

`POST /api/v1/birth-profiles/validate`, doğum profilini Pydantic ile doğrular ve
başarıda `{ "valid": true, "profile": { ... } }` döndürür. Veritabanına kayıt yapmaz.

`POST /api/v1/locations/resolve`, ülke, şehir ve isteğe bağlı ilçe bilgisini backend
üzerinden Nominatim/OpenStreetMap ile koordinatlara çözer. Sağlayıcı adresi, User-Agent
ve timeout `backend/.env` içindeki `GEOCODING_*` ayarlarıyla yapılandırılır. Nominatim'in
kullanım ve rate-limit politikasına uyulmalıdır; frontend sağlayıcıya doğrudan istek atmaz.
Geocoding endpoint'i timezone veya tarihsel UTC offset üretmez.

Sonraki bağımsız backend modülü olarak `POST /api/v1/timezones/resolve` eklendi:
koordinatlar → IANA timezone → tarihsel yerel saat → UTC. Geocoding yanıtı timezone
üretmez; bu yeni endpoint koordinat ve exact doğum saati alır. Bugünkü offset yerine
doğum tarihindeki IANA kuralları kullanılır. Kurulumda güncellenen requirements dosyalarını
yükleyin. DST hata/aday modelleri ve veri sınırları: [Timezone motoru](docs/timezone.md).

### Portlar ve ortam değişkenleri

| Servis | Port | Ayar |
| --- | --- | --- |
| Frontend | 3000 | npm scripts |
| Backend | 8000 | uvicorn `--port` |

Frontend `.env.local` içindeki `NEXT_PUBLIC_API_BASE_URL`, backend adresini belirler;
başlangıç değeri `http://localhost:8000` şeklindedir. Bu değer tarayıcıda görünürdür
ve secret içermez.

Backend `.env` dosyası `backend/` dizininden okunur. `APP_ENV=development` sadece
`http://localhost:3000` ve `http://127.0.0.1:3000` için CORS açar.
`APP_ENV=production` veya `test` durumunda CORS middleware eklenmez. Değişken
belirtilmezse varsayılan `production`'dır. İşletim sistemi ortam değişkenleri `.env`'yi ezer.
Production origin politikası gelecekte ayrıca tanımlanmalıdır.

`.env` ve `.env.*` dosyaları git tarafından yok sayılır; yalnızca `.env.example`
dosyaları sürümlenir. Secret veya API anahtarı gerekmez. `NEXT_PUBLIC_` önekli
değerler tarayıcıya açıktır; secret için kullanılmamalıdır.

## Kontroller

Frontend dizininde:

```powershell
npm run lint
npm run typecheck
npm test
npm run build
```

Backend dizininde:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
```

macOS/Linux: `.venv/bin/python -m pytest -q`.
Backend testleri health, CORS ve doğum profili doğrulama kurallarını; frontend testleri
form kurallarını ve API istek dönüşümünü doğrular.

### Bilinen araç uyarıları

TypeScript 6 ve ESLint 9 uyumlu sürümlere sabitlenmiştir. Mevcut Next.js React lint
eklentisi ESLint 10 ile çalışmadığından ESLint 9 kullanılmaktadır; npm bu sürüm için
bakım sonu uyarısı verir. Araç zinciri güncellenirken birlikte yükseltilmelidir.
Backend testleri geçer; Starlette'in httpx ve AnyIO kullanımı iki deprecation
uyarısı üretir. Bunlar test başarısızlığı değildir, bağımlılık güncellemesinde ele alınmalıdır.

Production frontend derlemesini yerelde açmak için `npm run build` ardından
`npm start` kullanın. Backend runtime bağımlılıkları `requirements.txt` içindedir;
`requirements-dev.txt` test araçlarını ayrıca ekler. Production çalıştırmada
`APP_ENV=production` kullanın ve `--reload` seçeneğini kaldırın.

Frontend testleri Node.js 22.6+ gerektirir; geliştirmede Node.js 24 ile doğrulandı.
Yeni test bağımlılığı eklenmeden Node'un test çalıştırıcısı kullanılır.

Tasarım temeli editorial archive / modern mysticism, ivory-mürekkep-bronz renkleri,
Cormorant Garamond + Manrope ve Code Line motifidir. Fontlar lisanslarıyla birlikte
projede bulunur ve `next/font/local` ile sunulur. Sistem fontları yalnız fallback'tir.
Ayrıntılar: [Mimari sınırlar](docs/architecture.md), [Frontend tasarım sistemi](docs/frontend-design.md).

Kurulum referansları: [Next.js](https://nextjs.org/docs/app/getting-started/installation),
[FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/),
[FastAPI testleri](https://fastapi.tiangolo.com/tutorial/testing/).
