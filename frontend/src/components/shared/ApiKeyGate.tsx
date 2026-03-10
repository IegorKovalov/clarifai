import { useState } from 'react';

interface Props {
  onSubmit: (key: string) => void;
  title?: string;
  description?: string;
}

export function ApiKeyGate({ onSubmit, title = 'Enter your API key', description }: Props) {
  const [value, setValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (trimmed) onSubmit(trimmed);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md">
        <div className="flex items-center justify-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-brand-600 flex items-center justify-center shadow-lg">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
            </svg>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
          <h1 className="text-xl font-semibold text-slate-900 mb-1">{title}</h1>
          {description && (
            <p className="text-sm text-slate-500 mb-6">{description}</p>
          )}

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                API Key
              </label>
              <input
                type="password"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="sk_..."
                className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition"
              />
            </div>
            <button
              type="submit"
              disabled={!value.trim()}
              className="w-full rounded-lg bg-brand-600 hover:bg-brand-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium py-2.5 transition"
            >
              Continue
            </button>
          </form>
        </div>

        <div className="flex items-center justify-center gap-4 mt-4">
          <a href="/chat" className="text-xs text-slate-400 hover:text-brand-600 transition">
            Customer Chat
          </a>
          <span className="text-slate-300">·</span>
          <a href="/admin" className="text-xs text-slate-400 hover:text-brand-600 transition">
            Admin Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}
