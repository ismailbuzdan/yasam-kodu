import assert from "node:assert/strict";
import test from "node:test";
import { profileRequest } from "../src/lib/api.ts";
import { emptyProfile, validateProfile } from "../src/lib/profile-validation.ts";

const today = "2026-09-15";
const valid = { ...emptyProfile, firstName: "Test", lastName: "Kullanıcı", birthDate: "2000-02-29", birthTime: "09:30", country: "Türkiye", city: "İstanbul" };

test("empty and whitespace-only required fields are rejected", () => {
  assert.deepEqual(Object.keys(validateProfile(emptyProfile, today)), ["firstName", "lastName", "birthDate", "birthTime", "country", "city"]);
  const errors = validateProfile({ ...valid, firstName: "  ", lastName: "\t", country: " ", city: " " }, today);
  assert.equal(Object.keys(errors).length, 4);
});

test("today is allowed; future dates and impossible calendar dates are rejected", () => {
  assert.deepEqual(validateProfile({ ...valid, birthDate: today }, today), {});
  for (const birthDate of ["2026-09-16", "2001-02-29", "2020-04-31", "0000-01-01", "2020-13-01", "not-a-date"]) {
    assert.ok(validateProfile({ ...valid, birthDate }, today).birthDate, birthDate);
  }
});

test("exact time requires birth time", () => {
  assert.equal(validateProfile({ ...valid, birthTime: "" }, today).birthTime, "Kesin doğum saatini girmelisin.");
  assert.deepEqual(validateProfile(valid, today), {});
});

test("exact time must be a 24-hour HH:mm value", () => {
  for (const birthTime of ["24:00", "12:60", "9:30", "12:00:00", "invalid"]) assert.ok(validateProfile({ ...valid, birthTime }, today).birthTime);
  for (const birthTime of ["00:00", "23:59", "09:30"]) assert.deepEqual(validateProfile({ ...valid, birthTime }, today), {});
});

test("approximate intervals require a start and end time", () => {
  assert.equal(validateProfile({ ...valid, certainty: "approximate" }, today).timeStart, "Tahmini başlangıç saatini girmelisin.");
  assert.equal(validateProfile({ ...valid, certainty: "approximate", timeStart: "08:00" }, today).timeEnd, "Tahmini bitiş saatini girmelisin.");
  assert.deepEqual(validateProfile({ ...valid, certainty: "approximate", timeStart: "08:00", timeEnd: "09:30" }, today), {});
});

test("approximate intervals must be valid and chronological", () => {
  assert.ok(validateProfile({ ...valid, certainty: "approximate", timeStart: "10:00", timeEnd: "09:00" }, today).timeEnd);
  assert.ok(validateProfile({ ...valid, certainty: "approximate", timeStart: "25:00" }, today).timeStart);
});

test("unknown time does not require time information", () => {
  assert.deepEqual(validateProfile({ ...valid, certainty: "unknown", birthTime: "bad", timeStart: "bad", timeEnd: "bad" }, today), {});
});

test("API request uses the shared snake_case profile contract and clears unused times", () => {
  assert.deepEqual(profileRequest(valid), {
    first_name: "Test", last_name: "Kullanıcı", birth_date: "2000-02-29", birth_time: "09:30",
    country: "Türkiye", city: "İstanbul", district: null, time_accuracy: "exact",
    approximate_start_time: null, approximate_end_time: null,
  });
  assert.deepEqual(profileRequest({ ...valid, certainty: "approximate", timeStart: "08:00", timeEnd: "09:00" }), {
    first_name: "Test", last_name: "Kullanıcı", birth_date: "2000-02-29", birth_time: null,
    country: "Türkiye", city: "İstanbul", district: null, time_accuracy: "approximate",
    approximate_start_time: "08:00", approximate_end_time: "09:00",
  });
  assert.deepEqual(profileRequest({ ...valid, certainty: "unknown", birthTime: "09:30", timeStart: "08:00", timeEnd: "09:00" }), {
    first_name: "Test", last_name: "Kullanıcı", birth_date: "2000-02-29", birth_time: null,
    country: "Türkiye", city: "İstanbul", district: null, time_accuracy: "unknown",
    approximate_start_time: null, approximate_end_time: null,
  });
});
