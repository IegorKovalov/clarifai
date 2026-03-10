import { useCallback, useEffect, useState } from 'react';
import { ApiKeyGate } from '../components/shared/ApiKeyGate';
import { StatsGrid } from '../components/admin/StatsGrid';
import { FileUpload } from '../components/admin/FileUpload';
import { UrlIngest } from '../components/admin/UrlIngest';
import { fetchStats, fetchTenantInfo } from '../services/api';
import type { AdminStats, TenantInfo } from '../types';
import { Link } from 'react-router-dom';

const STORAGE_KEY = 'clarifai_api_key';

type Toast = { id: number; type: 'success' | 'error'; message: string };

export default function AdminPage() {
  const [apiKey, setApiKey] = useState(() => localStorage.getItem(STORAGE_KEY) ?? '');
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [tenant, setTenant] = useState<TenantInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [activeTab, setActiveTab] = useState<'file' | 'url'>('file');

  const addToast = useCallback((type: 'success' | 'error', message: string) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000);
  }, []);

  const loadData = useCallback(async () => {
    if (!apiKey) return;
    setLoading(true);
    try {
      const [s, t] = await Promise.all([fetchStats(apiKey), fetchTenantInfo(apiKey)]);
      setStats(s);
      setTenant(t);
    } catch (err) {
      addToast('error', err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, [apiKey, addToast]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleApiKey = (key: string) => {
    localStorage.setItem(STORAGE_KEY, key);
    setApiKey(key);
  };

  const handleLogout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setApiKey('');
    setStats(null);
    setTenant(null);
  };

  if (!apiKey) {
    return (
      <ApiKeyGate
        onSubmit={handleApiKey}
        title="Admin Dashboard"
        description="Enter your API key to access the tenant dashboard."
      />
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3.5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center shadow">
              <svg className="w-[18px] h-[18px] text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
              </svg>
            </div>
            <div>
              <h1 className="text-sm font-semibold text-slate-900 leading-none">ClarifAI Admin</h1>
              {tenant && <p className="text-xs text-slate-400 mt-0.5">{tenant.name}</p>}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/chat"
              className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-brand-600 px-2.5 py-1.5 rounded-lg hover:bg-slate-100 transition"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
              </svg>
              Chat
            </Link>
            <button
              onClick={loadData}
              disabled={loading}
              className="inline-flex items-center gap-1.5 text-sm text-slate-600 hover:text-brand-600 disabled:opacity-40 transition"
              title="Refresh stats"
            >
              <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
              </svg>
              Refresh
            </button>
            <button
              onClick={handleLogout}
              className="text-sm text-slate-400 hover:text-slate-600 transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* Stats */}
        <section>
          <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">Overview</h2>
          {stats ? (
            <StatsGrid stats={stats} />
          ) : (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-white rounded-2xl border border-slate-200 p-5 h-24 animate-pulse">
                  <div className="h-3 bg-slate-200 rounded w-1/2 mb-3" />
                  <div className="h-7 bg-slate-200 rounded w-1/3" />
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Tenant info */}
        {tenant && (
          <section>
            <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">Tenant Details</h2>
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5">
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
                {[
                  { label: 'Name', value: tenant.name },
                  { label: 'Bot name', value: tenant.bot_name },
                  { label: 'Status', value: tenant.is_active ? 'Active' : 'Inactive' },
                  { label: 'Escalation email', value: tenant.escalation_email ?? '—' },
                  { label: 'API Key', value: `${tenant.api_key.slice(0, 12)}…` },
                  { label: 'Created', value: new Date(tenant.created_at).toLocaleDateString() },
                ].map(({ label, value }) => (
                  <div key={label}>
                    <dt className="text-xs text-slate-500 font-medium">{label}</dt>
                    <dd className="text-sm text-slate-900 mt-0.5 font-mono">{value}</dd>
                  </div>
                ))}
              </dl>
            </div>
          </section>
        )}

        {/* Knowledge base ingestion */}
        <section>
          <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">Knowledge Base</h2>
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            {/* Tabs */}
            <div className="flex gap-1 mb-5 bg-slate-100 rounded-lg p-1 w-fit">
              {(['file', 'url'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-1.5 rounded-md text-sm font-medium transition ${
                    activeTab === tab
                      ? 'bg-white text-slate-900 shadow-sm'
                      : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  {tab === 'file' ? '📄 Upload File' : '🔗 Ingest URL'}
                </button>
              ))}
            </div>

            {activeTab === 'file' ? (
              <FileUpload
                apiKey={apiKey}
                onSuccess={(msg) => { addToast('success', msg); loadData(); }}
                onError={(msg) => addToast('error', msg)}
              />
            ) : (
              <div className="space-y-2">
                <p className="text-sm text-slate-500">Enter a public URL to fetch and index its content.</p>
                <UrlIngest
                  apiKey={apiKey}
                  onSuccess={(msg) => { addToast('success', msg); loadData(); }}
                  onError={(msg) => addToast('error', msg)}
                />
              </div>
            )}
          </div>
        </section>
      </main>

      {/* Toast stack */}
      <div className="fixed bottom-5 right-5 flex flex-col gap-2 z-50">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`flex items-start gap-3 max-w-sm rounded-xl px-4 py-3 shadow-lg border text-sm animate-slide-up ${
              t.type === 'success'
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                : 'bg-red-50 border-red-200 text-red-800'
            }`}
          >
            {t.type === 'success' ? (
              <svg className="w-4 h-4 mt-0.5 flex-shrink-0 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : (
              <svg className="w-4 h-4 mt-0.5 flex-shrink-0 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
              </svg>
            )}
            {t.message}
          </div>
        ))}
      </div>
    </div>
  );
}
