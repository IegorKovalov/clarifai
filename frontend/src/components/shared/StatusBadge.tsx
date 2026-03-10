interface Props {
  status: 'disconnected' | 'connecting' | 'connected' | 'error';
}

const config = {
  connected:    { dot: 'bg-emerald-400', label: 'Connected',    text: 'text-emerald-700' },
  connecting:   { dot: 'bg-amber-400 animate-pulse', label: 'Connecting…', text: 'text-amber-700' },
  disconnected: { dot: 'bg-slate-400', label: 'Disconnected', text: 'text-slate-500' },
  error:        { dot: 'bg-red-400',   label: 'Error',         text: 'text-red-600' },
};

export function StatusBadge({ status }: Props) {
  const c = config[status];
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${c.text}`}>
      <span className={`w-2 h-2 rounded-full ${c.dot}`} />
      {c.label}
    </span>
  );
}
