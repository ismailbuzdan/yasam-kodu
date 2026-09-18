import type { FieldName, ProfileErrors, ProfileValues, TimeCertainty } from "./profile-validation";

export const BIRTH_PROFILE_SESSION_KEY = "yasam-kodu:birth-profile";

export type BirthProfile = {
  first_name: string;
  last_name: string;
  birth_date: string;
  birth_time: string | null;
  country: string;
  city: string;
  district: string | null;
  time_accuracy: TimeCertainty;
  approximate_start_time: string | null;
  approximate_end_time: string | null;
};

type BirthProfileValidationResponse = {
  valid: true;
  profile: BirthProfile;
};

type ApiValidationDetail = {
  loc?: unknown[];
  msg?: string;
};

const fieldNameMap: Record<string, FieldName> = {
  first_name: "firstName",
  last_name: "lastName",
  birth_date: "birthDate",
  birth_time: "birthTime",
  country: "country",
  city: "city",
  district: "birthPlace",
  approximate_start_time: "timeStart",
  approximate_end_time: "timeEnd",
};

export class BirthProfileApiError extends Error {
  readonly fieldErrors: ProfileErrors;

  constructor(message: string, fieldErrors: ProfileErrors = {}) {
    super(message);
    this.name = "BirthProfileApiError";
    this.fieldErrors = fieldErrors;
  }
}

export function profileRequest(values: ProfileValues): BirthProfile {
  const isExact = values.certainty === "exact";
  const isApproximate = values.certainty === "approximate";
  return {
    first_name: values.firstName.trim(),
    last_name: values.lastName.trim(),
    birth_date: values.birthDate,
    birth_time: isExact ? values.birthTime || null : null,
    country: values.country.trim(),
    city: values.city.trim(),
    district: values.birthPlace.trim() || null,
    time_accuracy: values.certainty,
    approximate_start_time: isApproximate ? values.timeStart || null : null,
    approximate_end_time: isApproximate ? values.timeEnd || null : null,
  };
}

function apiBaseUrl(): string {
  const value = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (!value) {
    throw new BirthProfileApiError("API adresi yapılandırılmadı. Lütfen daha sonra tekrar dene.");
  }
  return value.replace(/\/$/, "");
}

function validationError(payload: unknown): BirthProfileApiError {
  const details = typeof payload === "object" && payload !== null && Array.isArray((payload as { detail?: unknown }).detail)
    ? (payload as { detail: ApiValidationDetail[] }).detail
    : [];
  const fieldErrors: ProfileErrors = {};
  for (const detail of details) {
    const field = detail.loc?.at(-1);
    if (typeof field === "string" && fieldNameMap[field] && detail.msg) {
      fieldErrors[fieldNameMap[field]] = detail.msg.replace(/^Value error, /, "");
    }
  }
  return new BirthProfileApiError(
    Object.keys(fieldErrors).length ? "Bazı bilgileri kontrol etmelisin." : "Profil doğrulanamadı. Lütfen bilgileri kontrol et.",
    fieldErrors,
  );
}

export async function validateBirthProfile(values: ProfileValues): Promise<BirthProfile> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}/api/v1/birth-profiles/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(profileRequest(values)),
    });
  } catch (error) {
    if (error instanceof BirthProfileApiError) throw error;
    throw new BirthProfileApiError("Bağlantı kurulamadı. Bilgilerin korunuyor; lütfen tekrar dene.");
  }
  if (response.status === 422) throw validationError(await response.json().catch(() => null));
  if (!response.ok) throw new BirthProfileApiError("Profil şu anda doğrulanamadı. Bilgilerin korunuyor; lütfen tekrar dene.");
  const body: unknown = await response.json();
  if (!isBirthProfileValidationResponse(body)) {
    throw new BirthProfileApiError("Profil yanıtı beklenen biçimde değil. Lütfen tekrar dene.");
  }
  return body.profile;
}

export function isBirthProfile(value: unknown): value is BirthProfile {
  if (typeof value !== "object" || value === null) return false;
  const profile = value as Partial<BirthProfile>;
  return typeof profile.first_name === "string"
    && typeof profile.last_name === "string"
    && typeof profile.birth_date === "string"
    && typeof profile.country === "string"
    && typeof profile.city === "string"
    && ["exact", "approximate", "unknown"].includes(profile.time_accuracy ?? "");
}

function isBirthProfileValidationResponse(value: unknown): value is BirthProfileValidationResponse {
  return typeof value === "object" && value !== null
    && (value as { valid?: unknown }).valid === true
    && isBirthProfile((value as { profile?: unknown }).profile);
}
