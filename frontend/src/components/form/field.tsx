import type { InputHTMLAttributes } from "react";
type FieldProps = InputHTMLAttributes<HTMLInputElement> & { id: string; label: string; helper: string; error?: string };
export function Field({ id, label, helper, error, required, className = "", ...props }: FieldProps) {
  return <div className={"field " + className}>
    <label htmlFor={id}>{label}{required && <span className="required-label"> (zorunlu)</span>}</label>
    <input {...props} id={id} name={id} required={required} aria-invalid={error ? true : undefined} aria-describedby={id + "-hint" + (error ? " " + id + "-error" : "")} />
    <p className="field-hint" id={id + "-hint"}>{helper}</p>
    {error && <p className="field-error" id={id + "-error"}>{error}</p>}
  </div>;
}
