export function CodeLine({ index, label }: { index: string; label: string }) {
  return <div className="code-line" aria-hidden="true"><span>{index}</span><span className="code-rule" /><span>{label}</span></div>;
}
