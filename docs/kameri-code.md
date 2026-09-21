---
tags:
  - memory/kameri
  - research/methodology
---

# Kamerî Kod — Stage K0 methodology

Convention revision: `kameri-k0-v1`, 2026-09-20 (unchanged by K1A).
Start: `main` / `6250d347af39da04291af7412521664532a03363`.
Decision: ADR-017 in [[05_DECISIONS]]. Evidence: [[kameri-source-qualification]] and
[bibliography](references/kameri_sources.json). Source IDs below resolve there.

K0 is complete for the five **explicit project methods** below. This is methodology
readiness, not implemented or tested runtime accuracy. K1 can be separately scoped to those
methods with confirmed Arabic input. Automatic name rendering, stellar-mansion reconstruction
and interpretation are not implementation-ready. No K1 work is authorized by this document.

## Stage K1A implementation qualification — 2026-09-20

Separately authorized K1A deterministic core is complete in `backend/app/services/traditional/`.
K0 and ADR-017 conventions are unchanged. K1B API is complete; Stage 11 NOT STARTED.
Evidence, exact internal input boundaries, test results and limitations: [[kameri-verification]].
This implementation status does not promote the deferred historical/interpretive claims below.

- `calculate_hijri(date)` uses the supplied date, rejects datetime input and supports 1800–2100.
- `calculate_lunar(aware_utc)` produces Sun/Moon longitudes, directed elongation, native `pheno`
  fraction, centered phase label and numeric mansion result, computing the Moon once.
- `calculate_abjad(text, confirmed=True)` requires confirmation for that exact input and policy;
  calling code must renew confirmation after edits. No original/normalized text in the result.
- `calculate_planetary_hour(aware_utc, latitude, longitude, timezone_id)` uses the existing pinned
  zone loader, native lock and initializer. It does not infer a zone or invoke AstrologyService.
- Pure phase/mansion helpers accept `[0,360]` (360 wraps to 0), rejecting negative/nonfinite or
  larger input. Hour membership uses exact rational representations of UT1 Julian-day floats.
- Frozen nested internal values expose mechanical provenance, not public transport schemas.
  Domain errors distinguish admission, unsupported text, native failure, invalid native results
  and unavailable solar events. No clock, network, persistence or interpretation in the package.

## Product and ownership boundary

UI name: **Kamerî Kod**. `traditional` remains a provisional internal umbrella, not a frozen
production identifier. This will be a separate module; Life Code v1 and Stage 10 contracts stay
unchanged. No endpoint, database, frontend, AI, PDF or new dependency is introduced in K0.

The module is not an Islamic ruling, fatwa, unseen knowledge or scientific personality measure.
It does not identify a person's true divine name, prescribe destiny or devotional practice.
Permitted wording includes “geleneksel eşleştirme”, “tarihî kaynaklarda”, “bu yönteme göre”,
“sembolik yorum”, “İslam kültür coğrafyasında kullanılan gelenek” and “ilişkilendirilen Esmâ”.
Prohibited wording includes “senin Esman”, “Allah'ın sana özel Esması”, “İslam'a göre kişiliğin”,
“gerçek zikrin”, “kaderin” and “şu kadar zikretmelisin”. This is a product boundary, not a fatwa.

Calculation produces values. Historical meaning requires separately qualified sources.
Astronomical precision cannot validate a symbolic interpretation. Every traditional interpretation
must have source IDs and a locator; a merely related article is not evidence for its formula.

## Common deterministic decisions — K-COMMON-01

These are PROJECT CONVENTIONS, owned by ADR-017 rather than attributed to historical sources.

- V1 mechanical scope: selected-method Hijri date, Moon phase/illumination, 28-sector mapping,
  confirmed-script abjad sum and seasonal planetary hours. No interpretation fields.
- Proposed support is Gregorian birth years 1800–2100 inclusive. This is an engineering limit,
  not a claim that every historical civil-time input in that range is known accurately.
- Gregorian input means the supplied proleptic Gregorian civil date. No automatic Julian/Rumi
  reinterpretation. An archival date in another calendar needs a separately qualified conversion.
- Use existing resolved UTC, WGS84 coordinates, IANA timezone identity and pinned historical
  tzdata. Do not infer today's offset, duplicate geocoding or resolve an ambiguous local time silently.
- Date-only Hijri conversion uses supplied local calendar date. Astronomy uses resolved UTC.
  Planetary-day ownership uses the resolved place and historical timezone. These are distinct owners.
- Unknown time produces no guessed UTC, phase, mansion or planetary hour. A standalone date
  calculation may use an actually supplied date; future orchestration/partial-result transport is unscoped.
- Floating-point astronomical positions are not rounded before classification. No epsilon shifts
  a value across a boundary. Non-finite values and unavailable native results fail explicitly.
- Planned native calls reuse the existing Astrology `_LOCK` and `initialize_ephemeris()` ownership
  also used by HD. Do not call the complete Astrology service merely to obtain Sun/Moon positions:
  that would introduce unrelated Placidus failures. No changes to existing engines in K0.

## Hicrî date — K-CAL-01 / K-CAL-02 / K-CAL-03

| Method | Determinism and range | Suitability and limit |
| --- | --- | --- |
| Actual crescent observation | Reproducible only with a specified recorded observation/authority dataset | Weather, location and acceptance rules matter; absent historical observations cannot be reconstructed as facts |
| Arithmetic/tabular civil | Fixed rules; algorithm can extend beyond any finite lookup table | Good for transparent symbolic date conversion, not a local proclamation |
| Umm al-Qura table | Deterministic for pinned table/version and covered dates | Saudi calendar correspondence; not automatically historical Turkish correspondence |
| Diyanet calculated calendar | Deterministic only with identified method revision and reference data | Contemporary institutional calendar; not an unchanging Ottoman backcast |

Sources CAL-01/02 distinguish the calendar families. CAL-03 describes historical discrepancies;
CAL-04 identifies current Turkish institutional practice. One-day differences can come from
epoch choice, visibility criterion, local/global observation or sunset versus midnight ownership.
**±1 day is not a guaranteed maximum**: CAL-03 discusses possible ±2-day discrepancies.
A library's reproducible answer is not a claim of religiously definitive dating.

**Chosen PROJECT CONVENTION:** `hijri_tabular_civil_friday_v1`, method version `1`.
Use local Gregorian **date correspondence at civil midnight**, not a sunset-adjusted instant.
The display must say “hesaplanmış/tabular Hicrî tarih”; it must not imply the historical local
date after sunset. Selecting date-only semantics avoids silently inventing a time for unknown births.

Arithmetic specification (CAL-02 for cycle/epoch; formula expressed independently here):

- AH year 1 begins on Julian 622-07-16, equivalent to proleptic Gregorian 622-07-19.
  Midnight JD is 1948439.5; its calendar-day JDN is 1948440. Never confuse noon JDN with midnight JD.
- Leap positions within each 30-year cycle: 2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29.
- Odd months have 30 days; even months 29; month 12 has 30 in a leap year.
- Days before AH year `y`: `354*(y-1) + floor((3+11*y)/30)`.
  Days before month `m`: `29*(m-1) + floor(m/2)`; add `d-1` to obtain day offset.
- Convert the supplied Gregorian calendar date to its integer calendar-day number; select the
  unique valid AH `(y,m,d)` whose offset plus 1948440 equals that number. No observational correction.
- Project metadata must identify method/version, `calendar_type=tabular_civil`, Friday epoch,
  leap-cycle ID, `day_boundary=local_civil_midnight`, input-calendar owner, supported range and
  limitations. This is provenance planning, not an API schema.

For historical Turkish births this is a defensible **calculated approximation**, not archival
certification. A product demanding the actual Ottoman/Turkish recorded date must instead qualify
a dated regional calendar/record; that capability is DEFERRED. Date-only conversion must not use
UTC's calendar date merely because UTC is already available in Life Code.

Package assessment: CAL-05 documents `hijridate 2.6.0`, Umm al-Qura, Gregorian 1924-08-01 through
2077-11-16 (inclusive), AH 1343–1500, MIT. It excludes much of the project range and does not implement
the chosen method. CAL-06 advertises `hijrical 1.3.1` arithmetic and visibility modes, unbounded
arithmetic and astronomical AH 1–1600; those are upstream claims, not K0-tested support. It also
contains a separate astronomy model, unnecessary for the existing Swiss stack. No package is selected
or installed. Prefer a small independently implemented arithmetic rule in K1, verified against
published calendar references, over adding either package to obtain a different calendar convention.

## Astronomical Moon — K-MOON-01 / K-MOON-02

Source AST-02 defines the four primary phase **events** by apparent longitude difference.
AST-01 documents the native position/illumination interface. Project method:
`moon_apparent_geocentric_v1`, version `1`, CALCULATED_ASTRONOMICAL.

Use existing pinned `pyswisseph 2.10.3.2 / Swiss 2.10.03`, explicit Moshier and existing initialization.
Resolved UTC converts through `utc_to_jd` into TT and UT1. Sun/Moon positions and `pheno` use TT;
rise/set calls below use UT1. Longitude is apparent, geocentric, tropical, ecliptic-of-date,
normalized into `[0,360)`. No topocentric Moon or sidereal offset in this method.

Directed elongation `E = (Moon longitude - Sun longitude) mod 360` is `[0,360)`; do not replace
it with unsigned 3D angular separation. Illumination is the `pheno(TT, MOON, MOSEPH)` returned
illuminated fraction `k` (attribute 1), checked finite and within `[0,1]`. The geometric relation
is `k=(1+cos(i))/2` for phase angle `i` at the Moon, not the directed longitude difference `E`.
Do not silently substitute `(1-cos(E))/2`; lunar latitude and actual geometry distinguish them.
Illumination is modeled geometric disk fraction, not weather-dependent visible brightness or eclipse shading.

Primary events occur at `E=0,90,180,270` (AST-02). Continuous display bins below are a separate
PROJECT CONVENTION `phase_bins_8_centered_v1`; “full-moon bin” does not assert exact opposition.

| Label | Owned directed elongation interval |
| --- | --- |
| new_moon | `[337.5,360)` union `[0,22.5)` |
| waxing_crescent | `[22.5,67.5)` |
| first_quarter | `[67.5,112.5)` |
| waxing_gibbous | `[112.5,157.5)` |
| full_moon | `[157.5,202.5)` |
| waning_gibbous | `[202.5,247.5)` |
| last_quarter | `[247.5,292.5)` |
| waning_crescent | `[292.5,337.5)` |

Equality belongs to the interval beginning at that boundary; 360 normalizes to 0. Do not round
to detect an exact event. No primary-event boolean or event-time solver is required in V1.
Lunar age is DEFERRED: if later included it must be elapsed time from the most recent solved
geocentric conjunction (including the instant itself), not `E/360 * 29.53`, Hijri day-of-month
or elapsed calendar days. Its solver tolerances must be separately frozen before implementation.
Age is not necessary for any of the five V1 calculations.

## 28 lunar mansions — K-MAN-01 / K-MAN-02

MAN-01 describes stellar/seasonal stations and a later equal-arc account. It is secondary evidence
for that history, not a directly collated original treatise. Distinguish:

| Model | Reference and limitation |
| --- | --- |
| Historical stellar/asterism stations | Named stars/groups and observational traditions; not automatically equal longitude intervals |
| Equal ecliptic sectors | Mathematical division with a separately chosen origin and frame |
| Modern lunar-mansion tables | May mix tropical/sidereal anchors, aliases and interpretations; not authoritative by agreement |

Stellar positions relative to the equinox change with precession. A historical reconstruction
would require a selected work/epoch, identified stars, coordinate/precession model and a rule
for boundaries between them. Picking a modern ayanamsha does not by itself reconstruct that work.
Longitude-only sectors omit star-group extent, latitude and visibility; they are symbolic indexing.

MAN-01 prints `12°50′`; 28 such arcs total only `359°20′`. This is a documented numerical discrepancy,
not a production constant. The exact equal width is `360/28 = 90/7` degrees, approximately
`12°51′25.714286″`. Historical universality of this exact width and a tropical zero anchor remains
UNVERIFIED. We do not claim al-Biruni or al-Qazwini prescribed our executable method.

**Chosen PROJECT CONVENTION:** `mansion_equal28_tropical_v1`, version `1`.
Use the Moon longitude above. Anchor 0° tropical Aries; index 1 owns `[0,90/7)`, index 28 owns
`[27*90/7,360)`. Index `j+1` owns `[j*90/7,(j+1)*90/7)` for `j=0..27`.
Interpret the computed binary64 longitude as its exact rational value for comparison with these
rational boundaries. Do not classify using rounded degree-minute labels or a rounded width.
Exactly representable boundaries 0°,90°,180°,270° belong to 1,8,15,22 respectively; wrap returns 1.
This is CALCULATED_SYMBOLIC with `mapping_kind=equal_ecliptic_sectors`, plus provenance for the
CALCULATED_ASTRONOMICAL longitude. It is not the Moon's closest named star or a Hijri day number.

### Proposed name display catalogue

This is a **documentation proposal**, not a production lookup dataset. Source MAN-01 supports
the sequence and Turkish name forms. Arabic spellings and romanization below are editorial
renderings of those names, not quotations from a verified Arabic edition; they remain
`PROPOSED_LABEL / Arabic-edition collation UNVERIFIED`. A later UI/name catalogue must qualify them
before publication. K1's qualified mechanical output is the sector index and method, not an
assertion of an exact historical name spelling. No interpretations are attached.

| Index | Arabic name (proposed) | Transliteration (editorial) | Turkish display (proposed) | source_ids |
| --- | --- | --- | --- | --- |
| 1 | الشرطان | al-Sharaṭān | Şeretân | MAN-01 |
| 2 | البطين | al-Buṭayn | Butayn | MAN-01 |
| 3 | الثريا | al-Thurayyā | Süreyyâ | MAN-01 |
| 4 | الدبران | al-Dabarān | Deberân | MAN-01 |
| 5 | الهقعة | al-Haqʿa | Hak‘a | MAN-01 |
| 6 | الهنعة | al-Hanʿa | Hen‘a | MAN-01 |
| 7 | ذراع الأسد | Dhirāʿ al-Asad | Zirâü’l-esed | MAN-01 |
| 8 | النثرة | al-Nathra | Nesre | MAN-01 |
| 9 | الطرف | al-Ṭarf | Tarf | MAN-01 |
| 10 | الجبهة | al-Jabha | Cebhe | MAN-01 |
| 11 | الزبرة | al-Zubra | Zübre | MAN-01 |
| 12 | الصرفة | al-Ṣarfa | Sarfe | MAN-01 |
| 13 | العواء | al-ʿAwwāʾ | Avvâ | MAN-01 |
| 14 | السماك الأعزل | al-Simāk al-Aʿzal | Simâkü’l-a‘zel | MAN-01 |
| 15 | الغفر | al-Ghafr | Gafr | MAN-01 |
| 16 | الزبانى | al-Zubānā | Zübânâ | MAN-01 |
| 17 | الإكليل | al-Iklīl | İklîl | MAN-01 |
| 18 | قلب العقرب | Qalb al-ʿAqrab | Kalbü’l-akreb | MAN-01 |
| 19 | الشولة | al-Shawla | Şevle | MAN-01 |
| 20 | النعائم | al-Naʿāʾim | Naâim | MAN-01 |
| 21 | البلدة | al-Balda | Belde | MAN-01 |
| 22 | سعد الذابح | Saʿd al-Dhābiḥ | Sa‘dü’z-zâbih | MAN-01 |
| 23 | سعد بلع | Saʿd Bulaʿ | Sa‘dü bülâ | MAN-01 |
| 24 | سعد السعود | Saʿd al-Suʿūd | Sa‘dü’s-suûd | MAN-01 |
| 25 | سعد الأخبية | Saʿd al-Akhbiya | Sa‘dü’l-ahbiyye | MAN-01 |
| 26 | الفرع الأول | al-Farʿ al-Awwal | Fer‘u’l-evvel | MAN-01 |
| 27 | الفرع الثاني | al-Farʿ al-Thānī | Fer‘u’s-sânî | MAN-01 |
| 28 | بطن الحوت | Baṭn al-Ḥūt | Batnü’l-hût | MAN-01 |

Alternative labels such as al-muqaddam/al-muʾakhkhar or al-rishāʾ must be documented as aliases
against their own source, not silently substituted into this proposed al-Qazwini-derived sequence.

## Ebced — K-ABJ-01 / K-ABJ-02

Choose `abjad_mashriqi_kabir_v1`, normalization `abjad_text_v1`, version `1`.
This is additive Eastern/Maşrık numeral notation, called büyük ebced here; no modulo,
digit reduction, personality derivation or Esmâ selection. “Al-jummal/hesâb-ı cümel” and “ebced”
have overlapping historical uses; neither label licenses every formula under that name.
ABJ-01 and ABJ-02 support values and variation, not a universal name destiny calculation.

The factual mapping is independently set out below (ABJ-01; ABJ-02 Table 2):

| Values | Letters in matching order |
| --- | --- |
| 1,2,3,4,5,6,7,8,9 | ا ب ج د ه و ز ح ط |
| 10,20,30,40,50,60,70,80,90 | ي ك ل م ن س ع ف ص |
| 100,200,300,400,500,600,700,800,900 | ق ر ش ت ث خ ذ ض ظ |
| 1000 | غ |

ABJ-02's Western notation differs: ص=60, ض=90, س=300, ظ=800, غ=900, ش=1000.
Other listed values agree. Do not auto-detect a region or mix systems. Manuscript evidence
does not imply that every historical author used the same conventions for names.

### Exact normalization order and decisions

Process confirmed Arabic-script input only; retain the original solely in request-local memory.
The following is an explicit PROJECT text policy grounded where stated, not a universal spelling rule.

1. Apply Unicode NFC, retaining meaningful hamza until the carrier mapping is complete (TXT-01).
   Do not strip all combining marks first or apply blanket NFKC.
2. Expand only lam-alif presentation ligatures U+FEF5–U+FEFC into their corresponding lam plus
   alif-with-madda/hamza/plain-alif sequence, then NFC again. Reject all other presentation forms,
   including whole-word ligatures; never expand them silently by unrestricted compatibility folding.
3. Apply the letter policy below. Combining hamza/madda left after NFC and outside a recognized
   composed carrier are unsupported, not deletable vowel signs.
4. Ignore only the listed vocalization marks/separators. Any other code point rejects the whole
   calculation; there is no best-effort partial sum. At least one counted letter is required.
5. Add retained letter values once each. No phonetic expansion or automatic Arabic article removal.

| Input | Numeric treatment | Evidence / ownership |
| --- | --- | --- |
| ة | ت = 400, not ه = 5 | ABJ-01 selected convention |
| ى | ي = 10, not ا = 1 | PROJECT glyph-based choice; ABJ-01 displays ya in undotted form, not proof of all alif-maqsura practice |
| أ إ آ | ا = 1 | ABJ-01; NFC must precede mark removal |
| ؤ ئ | ا = 1, not و = 6 or ي = 10 | ABJ-01 hamza irrespective of seat; carrier is not separately counted |
| ء | ا = 1 | ABJ-01 |
| ٱ | ا = 1 | PROJECT extension for alif-wasla; not asserted as a quoted historical rule |
| پ چ ژ ڭ | ب=2, ج=3, ز=7, ك=20 | ABJ-01 |
| ک ی | ك=20, ي=10 | PROJECT script-variant equivalence |
| گ | ك=20 | PROJECT extension, explicit and distinct from sourced ڭ; not all Ottoman traditions |
| U+064B–U+0652 | Ignore, including shadda; no consonant doubling | PROJECT written-letter, not spoken-letter count |
| U+0670, U+0640 | Ignore superscript alif and tatweel | PROJECT policy; superscript alif does not add 1 |
| U+0009, U+000A, U+000D, U+0020, U+00A0 | Ignore these whitespace characters only | PROJECT allowlist |
| U+0027, U+002C, U+002D, U+002E, U+2019, U+060C, U+061B, U+061F | Ignore these punctuation characters only | PROJECT allowlist |
| Latin letters, digits, emoji, ZWJ/ZWNJ, bidi controls, unlisted extended letters/marks/punctuation | Reject | PROJECT fail-closed policy; no value 0 or transliteration fallback |

Synthetic glyph checks, not personal-name fixtures: `ابج` → 6; `ة` → 400; `ؤئء` → 3;
`ى` → 10; `پچژڭ` → 32; written `ب` plus shadda → 2. These are hand-derived rule examples,
not third-party goldens. Final script and normalization policy must be visible to the user before
confirmation, since the handling of ة, ى, hamza and shadda can materially change the sum.

## Turkish → Arabic-script rendering — K-NAME-01

The qualified sources do **not establish one universal reversible standard** for turning arbitrary
modern Turkish Latin-script personal names into Arabic spelling. This is a bounded research finding,
not proof that no specialized scheme exists. TXT-02 covers Ottoman-to-Roman cataloging in the other
direction, including context and lexical forms; it cannot supply the missing information by inversion.

Distinguish letter transliteration, sound transcription, conventional Arabic spelling, historical
Ottoman orthography and a modern Arabic rendering of a Turkish name. An established Arabic-origin
given name can have a dictionary form; a newly formed Turkish surname may require choices about
vowels and consonants. A mechanical character map cannot guarantee both tasks equally.
No real user's name is used as an example in this public documentation.

**Chosen boundary:** ebced requires an explicitly user-confirmed Arabic-script form. Reconfirmation
is needed after edits or a normalization/method change. Confirmation means “this is the form to
calculate”, not linguistic, religious or historical certification. Do not automatically sum the
Latin `full_name` already supplied to Numerology, or silently reuse Numerology normalization.

Recommended later workflow: dictionary candidates with entry-specific source IDs + deterministic,
versioned project transcription suggestion → displayed Arabic form and counting policy → user edits
and confirms → deterministic ebced. Advantages: reproducible suggestions and visible ambiguity.
Disadvantages: non-readers may not be able to judge spelling; variant choices still change totals.
Allow declining the calculation; never make suggested spelling appear authoritative.

Automatic suggestion is **DEFERRED**, not a hidden K1 dependency. `tr_ar_v1` is a reserved proposal,
not an implemented or frozen algorithm. Before implementation, freeze dictionary licensing/version,
entry provenance, Turkish casing/tokenization, all letter/vowel rules, mixed-origin names, collisions,
unknown-token behavior and synthetic test vectors. Direct confirmed-script entry is the qualified
V1 ebced input path; this document does not design its frontend or API.

## Planetary hour — K-HOUR-01 / K-HOUR-02

HOUR-01 (Dio 37.18–19) supplies the seven-body sequence and weekday relation. HOUR-02 distinguishes
seasonal from ecliptic unequal hours; TRAD-03 describes first-hour sunrise ownership.
These sources do not establish one universally Islamic planetary-hour system.

Choose PROJECT method `planetary_hours_seasonal_v1`, version `1`:

- Cyclic order: Saturn → Jupiter → Mars → Sun → Venus → Mercury → Moon.
  “Chaldean order” is a conventional label, not a proven origin claim.
- Weekday first-hour rulers: Monday Moon, Tuesday Mars, Wednesday Mercury, Thursday Jupiter,
  Friday Venus, Saturday Saturn, Sunday Sun.
- For birth instant `t`, identify consecutive solar events `R0 < S0 < R1` such that
  `R0 <= t < R1`. Planetary day starts at `R0`, ends at `R1`; its weekday is the **local civil
  date of R0** in the already resolved IANA zone, not the UTC date or necessarily t's date.
- If t is before today's sunrise, use the previous sunrise's day ruler; local midnight does not
  reset the cycle. Exact sunrise begins a new planetary day; exact sunset begins night hour 1.
- Divide `[R0,S0)` into 12 equal elapsed intervals and `[S0,R1)` into 12 equal elapsed intervals.
  Day hour i (1–12) owns `[R0+(i-1)*(S0-R0)/12, R0+i*(S0-R0)/12)`; night is analogous.
  Total-hour offset h is 0–11 in daylight and 12–23 at night. Ruler is the cyclic entry h places
  after the planetary-day ruler. Thus 24 hours advances the next ruler by `24 mod 7 = 3` positions.
- “Hour” is temporal, not sixty minutes. Use UT1 JD event values and the instant's UT1 JD for
  membership, treating represented values as exact rationals for the subdivision comparisons.
  No repeated floating addition or equality epsilon. UTC/local strings are display projections;
  rounding to microseconds must not feed classification. Display rounding is half-even.

Astronomical event convention (AST-01 interface; constants below are PROJECT choices):
Swiss `rise_trans` for SUN, explicit Moshier, CALC_RISE / CALC_SET, upper limb, refraction enabled;
no DISC_CENTER or NO_REFRACTION bits. Use coordinates from the existing resolver, observer height
0 m, pressure explicitly 1013.25 hPa, temperature 15°C, unobstructed level horizon. These assumptions
are metadata, not actual weather/elevation. Mountain/building horizon and terrain dip are unmodeled.
Reusing Swiss avoids a second ephemeris; it does not qualify the new adapter without K1 tests.

A native “no event”/circumpolar result means unavailable, not midnight, noon, nearest latitude or
equal 60-minute substitution. Search at most 48 hours before and after t and require chronological
adjacent rise/set/rise, each daylight/night duration strictly between 0 and 24 hours and total
cycle between 0 and 48 hours. Otherwise return a documented unavailable condition. This deliberately
excludes seasonal polar bridging and pathological transitions. Native failures remain distinguishable
from a physically absent sunrise. Do not search months away to manufacture a day.

Historical timezone uncertainty can change the weekday label even if the astronomical events are
well defined. Reject unresolved fold/nonexistent local time upstream; never apply present-day UTC offset.
Future-date admission belongs to a later transport stage, not a hidden clock in the calculation.
Event times/boundaries are CALCULATED_ASTRONOMICAL; the rule assigning a planet is CALCULATED_SYMBOLIC
with HISTORICAL_TRADITION provenance. It is not an astronomical measurement of planetary influence.

## Provenance, classification, AI and privacy — K-POLICY-01

Each future result needs field-appropriate classification, method ID/version, source IDs, limitations
and calculation-stack versions. Record tzdata when local ownership matters; Unicode version for
text normalization; ephemeris/time model/flags for astronomy. Avoid one generic “traditional” flag
that makes calculated values and historical beliefs indistinguishable.

| Classification | Scope |
| --- | --- |
| CALCULATED_ASTRONOMICAL | Sun/Moon positions, elongation, illumination, phase events; model-derived rise/set and temporal boundaries |
| CALCULATED_CALENDAR | Selected-method Hijri date; no religious-certainty inference |
| CALCULATED_SYMBOLIC | Abjad sum, equal-sector index, planetary ruler assignment; explicit mapping kind |
| HISTORICAL_TRADITION | Source-specific meanings and historical associations, never automatically generated from arithmetic |
| MODERN_POPULAR | Modern unsourced associations, clearly separated and not production-rule evidence |

Eight-bin labels must additionally carry `label_policy=phase_bins_8_centered_v1`; the bins are
project discretization of astronomy, not newly discovered event durations. Project choices have
`rule_origin=PROJECT_CONVENTION`; tiers rate sources, not the truth of symbolic claims.

AI is absent in K0. Future AI receives only `calculated_result + qualified_source_fragments +
explicit interpretation policy`. It never calculates a date, position, mansion, sum or hour; never
invents Esmâ or meanings missing from the qualified source. A source ID alone is not permission
to fabricate supporting prose. Interpretation readiness remains separate from mechanical readiness.

ADR-013 applies: tracked examples/evidence must be synthetic. No real name, birth combination,
district or mother's name from conversations enters the repository. Bibliographic author names are
source attribution, not personal fixtures. Names and confirmed spellings are private request data:
no logs, error echoes, analytics, public fixtures or persistence by default. Confirmation can be
request-scoped; it does not require storing a personal history. Mother-name data is not collected.

## Stage K0 acceptance table

READY below means sufficiently specified **to implement and verify later**, not released, tested,
religiously authoritative or historically exhaustive. No interpretation is READY.

| Feature | Status | Chosen convention | Evidence tier | Remaining ambiguity | Implementation readiness |
| --- | --- | --- | --- | --- | --- |
| Hijri date | READY, project freeze | Friday tabular cycle; local civil date/midnight | A: CAL-01–04 | Actual historical local proclamation not recovered | YES for calculated date only |
| Moon phase | READY, project freeze | Swiss apparent geocentric; pheno fraction; separate 8-bin label | A: AST-01–02 | New adapter accuracy not tested; age excluded | YES, requires K1 validation |
| Lunar mansion | READY for numeric sectors | 28 equal tropical sectors, 0° anchor, exact rational intervals | B: MAN-01 + project decision | Historical stellar reconstruction and Arabic label collation UNVERIFIED | YES for index/method; NO for proposed label catalogue or historical mapping |
| Abjad | READY, project freeze | Eastern additive values; explicit text policy; confirmed Arabic input | B: ABJ-01–02; A: TXT-01 | Other traditions differ; unsupported scripts rejected | YES for selected convention |
| Turkish→Arabic rendering | DEFERRED automatic suggestion | User confirmation chosen; tr_ar_v1 not yet frozen | A: TXT-02, bounded inference | Dictionary and transcription rules unqualified | Confirmed-script input YES; auto suggestion NO |
| Planetary hour | READY, project freeze | Sunrise day; 12+12 seasonal intervals; fixed observing assumptions | A: HOUR-01/AST-01; B: HOUR-02/TRAD-03 | Weather, topography, polar/historical input limitations explicit | YES for scoped method |
| Huruf (K-TRAD-01) | RESEARCH_ONLY | None | B: TRAD-01 | Work/edition-specific rule absent | NO |
| Asma (K-TRAD-02) | RESEARCH_ONLY | No personal assignment formula | B: TRAD-02 | Universal ebced mapping unqualified | NO |
| Zodiac–Asma | UNQUALIFIED | None | No qualified formula | Fixed scriptural twelve-sign mapping not established | NO |
| Dhikr numbers (K-TRAD-04) | DEFERRED | No personalized instructions | B: TRAD-04 context only | Historical citation does not authorize prescription | NO |
| Yildizname (K-TRAD-03) | RESEARCH_ONLY | No unified engine | B: TRAD-03 | Distinct work/method families | NO |
| Mother-name methods | DEFERRED | No collection/calculation | No qualified required method | Source/necessity/consent unestablished | NO |

The five mechanical areas in the task are Hijri, Moon, mansion, abjad and planetary hour; rendering
is a separate input problem. K1 methodological readiness is **YES only for these scoped methods**,
including index-only mansion output and confirmed-script ebced. A K1 request including automatic
names, Arabic mansion labels or historical reconstruction is **NOT READY** until the corresponding
qualification is completed. This scope boundary must remain visible in handoffs.

## Future validation gates (no runtime tests added in K0)

- Calendar: independently sourced epoch/date pairs, all 30 cycle positions and month endings,
  leap transitions, Gregorian leap dates and local/UTC date differences. Test sunset non-adjustment.
- Moon: external phase-event and illumination references with method/time provenance; primary
  event versus label separation; all eight boundaries and adjacent representable values.
- Mansion: all 28 rational boundaries and adjacent binary64 values, wrap, 0/90/180/270 anchors;
  do not treat agreement with an internet table as historical validation.
- Abjad: all 28 letters, every accepted extension and Unicode canonical equivalent, ligatures,
  ignored marks, rejected controls/digits/scripts, empty result and confirmation invalidation.
- Hours: all seven weekdays, pre-sunrise and exact event boundaries, all 24 subdivisions,
  DST/fold/date-line cases, extreme latitudes, absent events and native errors. External event
  comparison must use matching limb, refraction, horizon and timescale assumptions.
- Cross-engine concurrent/native-state regressions and privacy checks are required when K1 adds
  native callers. Source-derived expected values stay independent from the implementation under test.
- Before any new runtime delivery: existing backend regression and pip check; frontend checks only
  if frontend changes. K0 itself validates documents/metadata and runtime-file absence only.

## Unresolved and deliberately excluded

No claim is made of complete historical coverage. Primary Arabic mansion editions and their
spellings have not been directly collated; historical star boundaries and epoch remain unresolved.
Auto transcription needs a licensed dictionary and exact project mapping. Personal Esmâ, zodiac–Esmâ,
prescribed counts and mother-name formulae remain unqualified. These are recorded exclusions,
not defaults awaiting silent implementation. New scope requires a new evidence-backed decision.

## K1B public mechanical contract

`POST /api/v1/kameri/calculate` exposes the completed K1A mechanics without changing ADR-017.
Required resolved inputs are `local_date`, `utc_datetime`, `latitude`, `longitude`, `timezone_id`,
`arabic_name` and literal-true `arabic_name_confirmed`. The supplied local date owns tabular Hijri;
the UTC instant owns lunar astronomy and planetary-hour membership; coordinates/timezone own solar
event and local planetary-date resolution; confirmed Arabic owns only abjad. No equality constraint
exists between the local date and UTC calendar date.

The response is `kameri-code-v1`, lists `hijri`, `lunar`, `abjad`, `planetary_hour`, and fixes
`interpretation_present=false`. It is an explicit public projection: submitted/normalized Arabic,
letter traces, raw solar events and Julian days, Fraction interval bounds, native flags and search
diagnostics are excluded. Failure is all-or-nothing with static input-independent errors. This makes
the scoped Kamerî mechanical API complete; automatic transcription, historical mansion names,
Hurûf/Esmâ/zodiac–Esmâ/dhikr/yıldıznâme and interpretation remain unqualified or deferred.

## K2A interpretation boundary (no mechanical change)

[[kameri-interpretation-qualification]] qualifies only four independently bounded arithmetic/cultural
fragments for future KB work; it does not change the K1B contract or admit historical mapping tables.
The separate research JSON is not a production KB. ADR-019 prohibits unqualified AI additions,
personal Asma and devotional prescriptions; mother's name remains uncollected. Numeric mansion
sectors still have no approved historical interpretation bridge. K2B and Stage 11 NOT STARTED.
