---
tags:
  - memory/core
---

# Yaşam Kodu — Project Memory

**Project:** yasam-kodu
**Status:** active
**Last updated:** 2026-09-26

Yaşam Kodu; astroloji, numeroloji ve Human Design hesaplamalarını tek kişisel profil altında
birleştirmeyi hedefleyen web uygulamasıdır. Sistem sembolik öz-farkındalık ve eğlence amaçlıdır;
tıbbi, psikolojik, hukuki ya da finansal karar aracı değildir.

Temel ilke: **Calculation != Interpretation.** Hesaplamalar deterministik motorlardan gelir;
AI yalnız doğrulanmış sonuçları anlatır.

Mevcut teknoloji: Next.js + TypeScript + App Router + Tailwind; FastAPI + Python + Pydantic;
offline IANA timezone çözümlemesi için timezonefinder, zoneinfo ve tzdata. Deterministik backend;
doğum profili, geocoding, tarihsel timezone, Astrology, Numerology, Human Design, Unified Life Code
ve ayrı bounded Kamerî mechanical/knowledge katmanlarını içerir. Stage 11 AI interpretation ve
Stage 12 report/PDF henüz başlamamıştır. Kamerî knowledge readiness yalnız üç kaynaklı Hicrî kültürel
parçada sınırlıdır; hesaplama ve yorum ayrımı korunur.

Başlangıç noktaları: [[01_PRODUCT_VISION]], [[02_ARCHITECTURE]], [[03_ROADMAP]],
[[04_CURRENT_STATE]], [[05_DECISIONS]], [[06_API_CONTRACTS]], [[07_TEST_STRATEGY]],
[[08_AI_INTERPRETATION]], [[09_REPORT_DESIGN]], [[10_KNOWN_ISSUES]] ve [[CHANGELOG]].
Ayrıntılı mevcut kaynaklar: [timezone](timezone.md),
[frontend design](frontend-design.md), [erken mimari notu](architecture.md).
