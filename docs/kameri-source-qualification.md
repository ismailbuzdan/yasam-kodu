---
tags:
  - research/provenance
  - memory/kameri
---

# Kamerî Kod — source qualification

Research date: 2026-09-20. Methodology: [[kameri-code]]. Bibliographic records:
[kameri_sources.json](references/kameri_sources.json). This is a claim audit, not a corpus of
historical interpretations or production lookup data. No source code or long source text is copied.

## Evidence policy

Tier A covers primary historical works/critical editions, official institutions and scientific
standards **within their actual remit**. Tier B covers peer-reviewed studies, academic books,
university research/reference material and TDV encyclopedia articles. Tier C covers secondary/popular
explanations and, conservatively, self-published implementation documentation. Tier D covers blogs,
forums/social media and unsupported esoteric claims; it cannot set a production rule.

Source type is independent of tier. For example AST-01 is authoritative for its own astronomy
interface, not an independent astronomical validation. A library's documentation is primary evidence
of what its maintainer claims, but not a scientific or religious authority. Hosting a book at a
university does not automatically turn every statement into Tier A evidence.

Statuses: `VERIFIED_SUPPORT` means the cited passage was inspected and supports the bounded claim;
`PROJECT_CONVENTION` means a deliberate project choice; `UNVERIFIED` means not checked;
`UNQUALIFIED` means evidence does not justify the requested production claim. Evidence qualification
does not endorse religious, astrological or personality claims.

There are **19 source records: 9 A, 8 B, 2 C, 0 D**. Multiple URLs for one work/release count once.
These are not 19 independent implementations or 19 qualified traditional formulas. Two entries use
indexed passage evidence with explicit retrieval limits below; no inaccessible source is treated as
having been fully read. Publication dates, not search-engine crawl ages, determine bibliography years.
Unknown dates are null, never guessed.

## Claim-to-source ledger

Each rule in the methodology references a claim ID and these source IDs. Engineering choices are
not disguised as quotations or as rules discovered by implementation majority vote.

| Claim ID / claim | Source and tier | What it supports | What it does NOT support / decision |
| --- | --- | --- | --- |
| K-CAL-01: arithmetic Hijri is reproducible | [CAL-01 USNO](https://aa.usno.navy.mil/faq/islamic), [CAL-02 Richards §15.6.3](https://aa.usno.navy.mil/downloads/c15_usb_online.pdf), A | Month lengths, explicit cycle and epoch | Religious or Turkish historical certainty; local-midnight admission is PROJECT_CONVENTION |
| K-CAL-02: historical/civil dates may disagree | [CAL-03 TTK](https://ttk.gov.tr/tarih-cevirme-kilavuzu/), [CAL-04 Diyanet](https://kurul.diyanet.gov.tr/tr/faaliyetler/2020-2025/ibadet-vakitleri-dini-gun-ve-gecelerin-tespiti/kameri-hicri-ay-baslarinin-tespiti), A | Historical discrepancy and contemporary institutional process | A guarantee of only ±1 day, or one formula for all Turkish history |
| K-CAL-03: candidate package methods/ranges | [CAL-05 HijriDate](https://pypi.org/project/hijridate/), [CAL-06 hijrical](https://pypi.org/project/hijrical/), C | Upstream documentation/release claims | Independent accuracy, religious authority or dependency approval; neither selected |
| K-MOON-01: positions and disk fraction | [AST-01 Swiss manual §§8.12–13](https://www.astro.com/swisseph/swephprg.htm), A | Native phenomena/rise-set interface | Project integration correctness, empirical brightness or interpretation |
| K-MOON-02: exact phase events versus bins/age | [AST-02 USNO](https://aa.usno.navy.mil/faq/moon_phases), A | Longitude-difference event definitions and age concept | Centered 45° display bins; those are PROJECT_CONVENTION; age excluded |
| K-MAN-01: different mansion models | [MAN-01 ENVÂ’](https://islamansiklopedisi.org.tr/enva), B | Stellar tradition and secondary account of equal arcs | Exact universal width, epoch or tropical origin; numerical discrepancy preserved |
| K-MAN-02: equal-sector mapping and labels | MAN-01, B; ADR-017 | Name sequence context | `0° + 28 equal tropical sectors` is PROJECT_CONVENTION; Arabic labels are an editorial proposal, not a collated edition |
| K-ABJ-01: Eastern values, Western differences | [ABJ-01 EBCED](https://islamansiklopedisi.org.tr/ebced), [ABJ-02 George p.92](https://www.pure.ed.ac.uk/ws/files/8185735/E146535910900059X.pdf), B | Actual numeral systems differ | One universal mystical/personality function |
| K-ABJ-02: normalize without losing hamza | ABJ-01, B; [TXT-01 Unicode](https://www.unicode.org/versions/Unicode16.0.0/core-spec/chapter-9/), A | Selected historical correspondences and encoded character distinctions | Unicode has no ebced arithmetic; extension/allowlist policy is project-owned |
| K-NAME-01: confirmed spelling required | [TXT-02 ALA-LC](https://www.loc.gov/catdir/cpso/romanization/ottoman.pdf), A | A context-dependent romanization standard in the opposite direction | Unique arbitrary Latin→Arabic reconstruction; confirmation is PROJECT_CONVENTION |
| K-HOUR-01: cyclic rulers and weekday | [HOUR-01 Dio 37.18–19](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Cassius_Dio/37%2A.html), A; [TRAD-03](https://islamansiklopedisi.org.tr/yildizname), B | Seven-body sequence/day relation; sunrise context in described tradition | Unique Islamic algorithm, guaranteed Chaldean origin or favorable-action advice |
| K-HOUR-02: temporal intervals and sunrise model | [HOUR-02 Queens’ College](https://history.queens.cam.ac.uk/college/virtual-dial), B; AST-01, A | Seasonal/ecliptic distinction and available solar-event calculation | Project atmospheric assumptions or polar fallback; no fallback is selected |
| K-TRAD-01: huruf requires a work-specific method | [TRAD-01 HURÛF](https://islamansiklopedisi.org.tr/huruf), B | Historical diversity | A deployable personality engine |
| K-TRAD-02: personal Asma mapping unqualified | [TRAD-02 ESMÂ-i HÜSNÂ](https://islamansiklopedisi.org.tr/esma-i-husna), B | Distinct lists/classifications | Universal name-sum mapping or scriptural twelve-sign mapping |
| K-TRAD-03: yıldızname is a family of works | TRAD-03, B | Distinct approaches and literature | A single complete algorithm or a justified need to collect a mother's name |
| K-TRAD-04: devotional context is not prescription | [TRAD-04 ZİKİR §1](https://islamansiklopedisi.org.tr/zikir#1), B | Religious/historical background | Personalized repetition counts from arithmetic |
| K-COMMON-01 / K-POLICY-01 | ADR-001/013/017 and user scope | Project ownership, classification, privacy and limits | Not externally attested historical conventions |

## Access and independent-source limits

Most source passages were retrieved directly as web text. CAL-02 and ABJ-02 were read as PDF text
with section/page locators. CAL-03 retrieved successfully before a later repeated request failed;
its discrepancy statement was also visible in indexed text. TXT-02 rules 9–10 were available in
indexed PDF text, and the official table index/collection guide were checked; direct PDF retrieval
failed. This is not full-table collation. No rule depends on copying that table or asserting a
Latin-to-Arabic inverse. These limitations are recorded in the bibliography.

The user-requested Turkish→Arabic “single universal standard” was not established in this search.
The negative conclusion is deliberately bounded: known romanization is insufficient for unique
reverse spelling. A general absence theorem was not proven. The safe implementable boundary is
confirmed Arabic input; an automatic algorithm remains DEFERRED.

No library was executed or compared on a newly collected chart in K0. No fresh independent
astronomy accuracy measurements, source hashes or golden fixtures are claimed. Existing Stage 7/9
qualification does not automatically qualify future `pheno` or sunrise adapters. Public documentation
is adequate to choose their method; K1 must qualify their implementation with field-matched evidence.

## Historical follow-up candidates — not counted as inspected rule sources

These are discovery leads, not extra Tier A votes or directly read primary editions:

| Candidate | Locator obtained / why relevant | Current limitation |
| --- | --- | --- |
| al-Biruni, Kitab al-Tafhim | ABJ-01 bibliography points to London 1934 and Tehran 1983–84 editions | Primary pages not inspected; no exact mansion anchor attributed to it |
| al-Qazwini, Aja’ib al-makhluqat | MAN-01 attributes a 28-name sequence to this work | Edition/Arabic name collation UNVERIFIED; no manuscript ID invented |
| Ibn Asim, Kitab al-Anwa wa-l-azmina | MAN-01 bibliography: TSMK III. Ahmed 3508; facsimile Fuat Sezgin, Frankfurt 1985 | Catalogue citation reported by secondary source, not directly checked |
| Savage-Smith / Belloli, Islamicate Celestial Globes (1985) | [Smithsonian record](https://repository.si.edu/handle/10088/2445), DOI 10.5479/si.00810258.46.1 | Catalogue verified; full PDF retrieval failed/size-limited; substantive pages not qualified here |
| Thomas L. Lentz, Collection Guide (2022) | [Yale collection page](https://peabody.yale.edu/explore/collections/history-science-technology/lentz-collection), indexed p.230 temporal-hour explanation | Direct PDF failed; unnecessary for chosen rules given Dio/Queens’ evidence; not counted |
| Risale-i Yildizname (Istanbul 1274/1858) | TRAD-03 bibliography, pp.1–12 | Primary work not read; mother-name requirement not inferred |
| Letter/Asma works discussed by TRAD-01/02 | Potential work-specific scholarship | No edition/rule passage qualified; no interpretation dataset extracted |

Search results from blogs, commercial calculators, forums and modern esoteric pages were not used
to select production rules. No candidate gains authority merely by agreeing with another calculator.
No modern zodiac–Asma list was promoted to a scriptural or universal table.

## Deferred feature qualification

“No single standard established” means this study did not qualify one; it is not an assertion
that every local tradition is identical or that no historical variant can exist.

| Feature | Historical basis | Single standard? | Candidate sources | Source quality | Privacy requirements | Religious-claim risk | Implementation readiness |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Huruf interpretation | Work-specific letter symbolism attested | Not established | TRAD-01 and its primary bibliography | B background; exact rules unqualified | No extra personal fields justified | High if beliefs are presented as measured personality | RESEARCH_ONLY |
| Personal Asma association | Divine-name literature exists | Universal ebced→Asma function not established | TRAD-02; edition-specific association sources still needed | B context, no qualified formula | No name retention; spelling consent would be needed | High: avoid personal divine assignment | RESEARCH_ONLY |
| Zodiac–Asma | Modern lists encountered; no qualified fixed scriptural correspondence | Not established | TRAD-02 is background only, not proof of a zodiac formula | Formula UNQUALIFIED | No new birth collection for an unqualified mapping | High: do not call it Qur’an/hadith-derived | UNQUALIFIED |
| Dhikr counts | Practices have historical/religious contexts | No personalized arithmetic prescription qualified | TRAD-04; any later historical count needs exact edition/page | B context only | No personalized ritual profile | Very high if numerical associations become instructions | DEFERRED |
| Yildizname | Multiple works and methods | No unified executable method established | TRAD-03; named primary works above | B survey; primary rules UNVERIFIED | Only necessary inputs after method-specific assessment | High if prediction/destiny is claimed | RESEARCH_ONLY |
| Mother-name methods | Candidate practices require specific verification | No required method qualified | No inspected passage establishes a V1 need | UNQUALIFIED requirement | Do not collect mother's name; future necessity and consent must be established | High if treated as universal ritual necessity | DEFERRED |

A historical association could later be shown as “this work associates X with Y”, with source ID,
edition, locator and limits. It must not become “you must repeat Y N times”. A source documenting
a practice does not validate that practice's effectiveness or authorize the product to prescribe it.

## Licensing and provenance acceptance

No dependency is added. CAL-05 MIT license was checked at its PyPI-reported publishing commit;
CAL-06 declares MIT and its repository license was inspected, but exact release-source equivalence
is not audited. These are candidates, not approved packages. A future addition requires pinned
artifact/dependency license review and project notice handling. Existing Swiss AGPL selection remains.

TDV text/images retain publisher rights. George's repository copy is marked CC BY-NC-ND; the paper
is linked, not bundled as AGPL content. No scans, source graphics, interpretive descriptions or
third-party algorithms are incorporated. Small factual symbol/value correspondences are independently
expressed; historical attribution is retained. Future interpretation fragments need a separate
rights/provenance review. Bibliographic access does not grant unrestricted republication.

The source model requires source_id, title, author/editor, publication_year (null if unknown),
publisher/institution, source_type, tradition, tier, language, URL, accessed_at, relevant_claims,
limitations and notes. Locators and edition/catalog IDs are added where actually verified.
Every future rule needs a claim ID, source IDs and rule origin; every independent expected output
additionally needs synthetic input, exact producer version/settings, raw evidence, SHA256 and a
clearly stated field-level acceptance scope. Shared Swiss results are integration checks, not
independent astronomy. Never manufacture a hash for uncaptured web evidence or regenerate an
expectation to match production output.

K0 freezes five narrow mechanical methods and the provenance/product boundary. Arabic mansion
labels, automatic name suggestions and all interpretive features stay outside that freeze.
Before broadening implementation, resolve the affected ambiguity with a new documented revision.

## K1A runtime evidence supplement

The original 19-source K0 bibliography and ADR-017 remain unchanged. Separately authorized
K1A now has field-scoped runtime checks and ten hashed artifact captures/excerpts, documented
in [[kameri-verification]]. K1-CAL adds a directly inspected primary calendar paper for one
in-range published correspondence; K1-JPL, K1-SWETEST and K1-USNO identify runtime producers.
These are not ten independent implementations or a historical interpretation corpus.
No third-party code, full paper, source graphics or interpretive text was copied into production.
