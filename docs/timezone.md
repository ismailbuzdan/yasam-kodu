---
tags:
  - memory/architecture
---

# Koordinattan tarihsel UTC'ye

`POST /api/v1/timezones/resolve` bağımsız bir backend endpoint'idir. Mevcut profil
ve geocoding akışına otomatik çağrı eklenmemiştir.

```json
{"latitude":39.9,"longitude":32.8,"birth_date":"1997-07-11","birth_time":"07:15"}
```

Akış: WGS84 koordinatı → offline timezonefinder kara poligonları → IANA kimliği
→ doğum tarihindeki zoneinfo kuralları → timezone-aware yerel tarih ve UTC.
İstek dış servise gitmez. Deniz koordinatlarında `timezone_not_found` döner.
`birth_time` offset içermeyen yerel saattir; eksik/unknown saat için varsayılan üretilmez.

Başarı yanıtında `resolved: true`, `status: valid`, `timezone`, `local_datetime`,
`utc_datetime`, `utc_offset_minutes`, `dst` ve `fold` bulunur. ISO 8601 UTC yanıtındaki
`Z`, `+00:00` ile eşdeğerdir. Offset dakika cinsinden sayıdır; eski tarihlerin saniyeli
offset'lerini kaybetmemek için kesirli olabilir.

`zoneinfo` verisi doğrudan sabitlenmiş `tzdata` paketinden okunur; Windows veya başka
bir işletim sisteminin kurulu tzdb sürümüne bağlı değildir. Bugünkü offset tarihsel
offset değildir. Örneğin İstanbul 1993 kışında UTC+2 iken 2026'da UTC+3 kullanır.

Her yerel saat için fold=0 ve fold=1 UTC'ye, ardından tekrar yerel saate çevrilir.
İki farklı geçerli UTC varsa `409 ambiguous_local_time`, iki adayın tamamıyla döner.
Hiçbir aday geri dönüşte aynı yerel saati vermiyorsa `422 nonexistent_local_time`
döner. Servis bir adayı sessizce seçmez veya saati ileri kaydırmaz.

Diğer hata kodları: `invalid_coordinates` (422), `invalid_datetime` (422),
`timezone_not_found` (404), `timezone_data_unavailable` (503).
Hatalar `detail.code` ve `detail.message` içerir; kütüphane hataları sızdırılmaz.

Bağımlılıklar Python 3.12/Windows üzerinde doğrulanmıştır: timezonefinder 8.3.0,
timezonefinder-data 1.2026.3 ve tzdata 2026.4. Poligon verisi ve IANA kuralları
ayrı veri kümeleridir. Güncel poligonlar tarihsel idari sınır değişikliklerini
yeniden oluşturmaz; sınır yakınları ve çok eski tarihler ayrıca değerlendirilmelidir.
Paket sürümü yükseltirken `tests/fixtures/birth_cases.json` regresyonları çalıştırılmalıdır.
Örnek ve fixture verileri tamamen sentetiktir; gerçek kişilerden alınmamıştır.
Beklenen UTC değerleri sabittir, test sırasında
servisin çıktısından türetilmez.

Kaynaklar: [timezonefinder kullanımı](https://timezonefinder.readthedocs.io/en/latest/1_usage.html),
[Python zoneinfo ve fold](https://docs.python.org/3.12/library/zoneinfo.html).
