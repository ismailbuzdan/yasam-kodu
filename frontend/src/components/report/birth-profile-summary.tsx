"use client";

import Link from "next/link";
import { useSyncExternalStore } from "react";
import { BIRTH_PROFILE_SESSION_KEY, isBirthProfile, type BirthProfile } from "@/lib/api";

const subscribe = () => () => {};
const serverSnapshot = () => null;

function clientSnapshot(): string | null {
  return sessionStorage.getItem(BIRTH_PROFILE_SESSION_KEY);
}

function upper(value: string): string {
  return value.toLocaleUpperCase("tr-TR");
}

function formattedDate(value: string): string {
  const parsed = new Date(`${value}T12:00:00`);
  return upper(new Intl.DateTimeFormat("tr-TR", { day: "numeric", month: "long", year: "numeric" }).format(parsed));
}

function timeLabel(profile: BirthProfile): string {
  if (profile.time_accuracy === "exact") return profile.birth_time ?? "—";
  if (profile.time_accuracy === "approximate") return `YAKLAŞIK ${profile.approximate_start_time}–${profile.approximate_end_time}`;
  return "SAAT BİLİNMİYOR";
}

export function BirthProfileSummary() {
  const rawProfile = useSyncExternalStore(subscribe, clientSnapshot, serverSnapshot);
  let profile: BirthProfile | null = null;
  if (rawProfile) {
    try {
      const parsed: unknown = JSON.parse(rawProfile);
      profile = isBirthProfile(parsed) ? parsed : null;
    } catch {
      profile = null;
    }
  }
  if (!profile) {
    return <section className="report-profile-empty" aria-labelledby="profile-empty-title">
      <p className="eyebrow">PROFİL BULUNAMADI</p>
      <h2 id="profile-empty-title">Bu oturumda doğrulanmış<br /><em>bir doğum profili yok.</em></h2>
      <p>Analiz taslağını görmek için doğum bilgilerini doğrulamalısın.</p>
      <Link className="button" href="/analiz">Doğum bilgilerine git <span aria-hidden="true">↗</span></Link>
    </section>;
  }

  const location = [profile.district, profile.city, profile.country].filter((value): value is string => Boolean(value)).map(upper).join(" / ");
  return <dl className="report-profile" aria-label="Doğrulanmış doğum profili">
    <div><dt>AD SOYAD</dt><dd>{upper(`${profile.first_name} ${profile.last_name}`)}</dd></div>
    <div><dt>DOĞUM TARİHİ</dt><dd>{formattedDate(profile.birth_date)}</dd></div>
    <div><dt>SAAT / KESİNLİK</dt><dd>{timeLabel(profile)}</dd></div>
    <div><dt>DOĞUM YERİ</dt><dd>{location}</dd></div>
  </dl>;
}
