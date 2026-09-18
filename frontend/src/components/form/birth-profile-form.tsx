"use client";
import { useRef, useState, useSyncExternalStore, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Field } from "./field";
import { BirthProfileApiError, BIRTH_PROFILE_SESSION_KEY, validateBirthProfile } from "@/lib/api";
import { emptyProfile, validateProfile, type FieldName, type ProfileErrors, type ProfileValues, type TimeCertainty } from "@/lib/profile-validation";

const subscribe = () => () => {};
const clientReady = () => true;
const serverReady = () => false;

export function BirthProfileForm() {
  // Prevent native form submission before client-side validation is available.
  const ready = useSyncExternalStore(subscribe, clientReady, serverReady);
  const router = useRouter();
  const form = useRef<HTMLFormElement>(null);
  const [values, setValues] = useState<ProfileValues>(emptyProfile);
  const [errors, setErrors] = useState<ProfileErrors>({});
  const [announcement, setAnnouncement] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [requestError, setRequestError] = useState("");
  function fieldProps(name: FieldName) {
    return {
      id: name, value: values[name], error: errors[name],
      onInput: (event: FormEvent<HTMLInputElement>) => {
        const next = { ...values, [name]: event.currentTarget.value };
        setValues(next);
        setRequestError("");
        if (errors[name] || (name === "timeStart" && errors.timeEnd) || (name === "timeEnd" && errors.timeStart)) {
          const nextErrors = validateProfile(next);
          setErrors(previous => ({
            ...previous,
            [name]: nextErrors[name],
            ...(name === "timeStart" ? { timeEnd: nextErrors.timeEnd } : {}),
            ...(name === "timeEnd" ? { timeStart: nextErrors.timeStart } : {}),
          }));
        }
      },
      onBlur: () => setErrors(previous => ({ ...previous, [name]: validateProfile(values)[name] })),
    };
  }
  function changeCertainty(certainty: TimeCertainty) {
    setValues(previous => ({
      ...previous,
      certainty,
      birthTime: certainty === "exact" ? previous.birthTime : "",
      timeStart: "",
      timeEnd: "",
    }));
    setErrors(previous => ({ ...previous, birthTime: undefined, timeStart: undefined, timeEnd: undefined }));
    setRequestError("");
    setAnnouncement(certainty === "approximate" ? "Tahmini başlangıç ve bitiş saati alanları açıldı. İkisi de zorunlu." : certainty === "unknown" ? "Saat alanları temizlendi ve devre dışı. Saat bilgisi olmadan devam edebilirsin." : "Kesin saat seçildi. Doğum saati zorunlu.");
  }
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextErrors = validateProfile(values);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) {
      setAnnouncement(Object.keys(nextErrors).length + " alanda düzeltme gerekiyor. İlk hatalı alana yönlendirildin.");
      // Follow DOM order, including conditional time inputs.
      const firstInvalid = Array.from(form.current?.querySelectorAll<HTMLInputElement>("input") ?? []).find(input => nextErrors[input.id as FieldName]);
      firstInvalid?.focus();
      return;
    }
    setSubmitting(true);
    setRequestError("");
    setAnnouncement("Profil doğrulanıyor.");
    void validateBirthProfile(values)
      .then((profile) => {
        sessionStorage.setItem(BIRTH_PROFILE_SESSION_KEY, JSON.stringify(profile));
        router.push("/sonuc");
      })
      .catch((error: unknown) => {
        const apiError = error instanceof BirthProfileApiError
          ? error
          : new BirthProfileApiError("Profil doğrulanamadı. Bilgilerin korunuyor; lütfen tekrar dene.");
        setErrors(apiError.fieldErrors);
        setRequestError(apiError.message);
        setAnnouncement(apiError.message);
        const firstInvalid = Array.from(form.current?.querySelectorAll<HTMLInputElement>("input") ?? []).find(
          (input) => apiError.fieldErrors[input.id as FieldName],
        );
        firstInvalid?.focus();
        setSubmitting(false);
      });
  }
  return <form ref={form} className="profile-form" noValidate autoComplete="off" onSubmit={submit} aria-describedby="form-note">
    <div className="form-intro"><p className="micro">PROFİL BİLGİLERİ</p><p id="form-note">Zorunlu alanlar etiketlerinde belirtilir. Bilgilerin bu aşamada doğrulanır, kalıcı olarak kaydedilmez.</p></div>
    <p className="sr-only" role="status" aria-live="polite" aria-atomic="true">{announcement}</p>
    {requestError && <p className="field-error form-error" role="alert">{requestError}</p>}
    <fieldset><legend><span className="legend-index" aria-hidden="true">01</span>İsminle başlayalım.</legend><div className="form-grid">
      <Field {...fieldProps("firstName")} label="Ad" helper="Günlük hayatta kullandığın adın." required type="text" maxLength={100} />
      <Field {...fieldProps("lastName")} label="Soyad" helper="Soyadını tam olarak yaz." required type="text" maxLength={100} />
    </div></fieldset>
    <fieldset><legend><span className="legend-index" aria-hidden="true">02</span>O ilk an.</legend><div className="form-grid">
      <Field {...fieldProps("birthDate")} label="Doğum tarihi" helper="Gün, ay ve yıl olarak doğum tarihin." type="date" required />
      {values.certainty === "exact" && <Field {...fieldProps("birthTime")} label="Doğum saati" helper="24 saat biçiminde (örnek: 14:30)." type="time" step="60" required />}
    </div>
    <fieldset className="certainty-fieldset"><legend>Saat kesin mi?</legend><div className="certainty-options">{([
      ["exact", "Kesin"], ["approximate", "Yaklaşık"], ["unknown", "Bilmiyorum"],
    ] as const).map(([value, label]) => <label className="radio-option" key={value}><input type="radio" name="certainty" value={value} checked={values.certainty === value} onChange={() => changeCertainty(value)} /><span>{label}</span></label>)}</div></fieldset>
    {values.certainty === "approximate" && <div className="form-grid approximate-fields">
      <Field {...fieldProps("timeStart")} label="Tahmini saat başlangıcı" helper="Aynı gün içindeki en erken saat." type="time" step="60" required />
      <Field {...fieldProps("timeEnd")} label="Tahmini saat bitişi" helper="Aynı gün içindeki en geç saat." type="time" step="60" required />
    </div>}
    <aside className="time-note"><span className="micro">NEDEN SAAT BİLGİSİ?</span><p>Doğum saati; yükselen burç, evler ve Human Design gibi saat hassasiyeti yüksek hesaplamaları etkileyebilir.</p></aside>
    </fieldset>
    <fieldset><legend><span className="legend-index" aria-hidden="true">03</span>Başladığın yer.</legend><div className="form-grid">
      <Field {...fieldProps("country")} label="Ülke" helper="Doğduğun ülke. Örnek: Türkiye." type="text" required maxLength={100} />
      <Field {...fieldProps("city")} label="Şehir" helper="Doğduğun şehir. Örnek: İstanbul." type="text" required maxLength={100} />
      <Field {...fieldProps("birthPlace")} className="field-wide" label="İlçe / Doğum yeri" helper="İsteğe bağlı. Örnek: Kadıköy." type="text" maxLength={200} />
    </div></fieldset>
    <div className="form-submit"><p>Bir başlangıç taslağı.<br /><span>Henüz gerçek analiz oluşturulmaz.</span></p><button type="submit" className="button" disabled={!ready || submitting}>{submitting ? "PROFİL DOĞRULANIYOR" : "YAŞAM KODUMU OLUŞTUR"}<span aria-hidden="true">↗</span></button></div>
    <noscript><p className="field-error">Bu formu kullanmak için tarayıcında JavaScript açık olmalı.</p></noscript>
  </form>;
}
