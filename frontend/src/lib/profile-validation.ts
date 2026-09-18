export type TimeCertainty = "exact" | "approximate" | "unknown";
export type ProfileValues = {
  firstName: string; lastName: string; birthDate: string; birthTime: string;
  timeStart: string; timeEnd: string; country: string; city: string;
  birthPlace: string; certainty: TimeCertainty;
};
export type FieldName = Exclude<keyof ProfileValues, "certainty">;
export type ProfileErrors = Partial<Record<FieldName, string>>;
export const emptyProfile: ProfileValues = {
  firstName: "", lastName: "", birthDate: "", birthTime: "", timeStart: "",
  timeEnd: "", country: "", city: "", birthPlace: "", certainty: "exact",
};
export function localToday(now = new Date()): string {
  return now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0") + "-" + String(now.getDate()).padStart(2, "0");
}
export function validateProfile(values: ProfileValues, today = localToday()): ProfileErrors {
  const errors: ProfileErrors = {};
  if (!values.firstName.trim()) errors.firstName = "Adını yazmalısın.";
  if (!values.lastName.trim()) errors.lastName = "Soyadını yazmalısın.";
  if (!values.birthDate) errors.birthDate = "Doğum tarihini girmelisin.";
  else {
    const parsed = new Date(values.birthDate + "T12:00:00");
    if (!/^\d{4}-\d{2}-\d{2}$/.test(values.birthDate) || values.birthDate.startsWith("0000") || Number.isNaN(parsed.getTime()) || localToday(parsed) !== values.birthDate) errors.birthDate = "Geçerli bir doğum tarihi girmelisin.";
    else if (values.birthDate > today) errors.birthDate = "Doğum tarihi gelecekte olamaz.";
  }
  const timePattern = /^([01]\d|2[0-3]):[0-5]\d$/;
  if (values.certainty === "exact") {
    if (!values.birthTime) errors.birthTime = "Kesin doğum saatini girmelisin.";
    else if (!timePattern.test(values.birthTime)) errors.birthTime = "Saati HH:mm biçiminde gir (örnek: 14:30).";
  }
  if (values.certainty === "approximate") {
    if (!values.timeStart) errors.timeStart = "Tahmini başlangıç saatini girmelisin.";
    else if (!timePattern.test(values.timeStart)) errors.timeStart = "Geçerli bir başlangıç saati gir (HH:mm).";
    if (!values.timeEnd) errors.timeEnd = "Tahmini bitiş saatini girmelisin.";
    else if (!timePattern.test(values.timeEnd)) errors.timeEnd = "Geçerli bir bitiş saati gir (HH:mm).";
    if (values.timeStart && values.timeEnd && !errors.timeStart && !errors.timeEnd && values.timeStart > values.timeEnd) errors.timeEnd = "Bitiş saati başlangıçtan önce olamaz. Aynı gün içinde bir aralık seç.";
  }
  if (!values.country.trim()) errors.country = "Doğduğun ülkeyi yazmalısın.";
  if (!values.city.trim()) errors.city = "Doğduğun şehri yazmalısın.";
  return errors;
}
