import type { AdminStats } from '../../types';

interface Props {
  stats: AdminStats;
}

interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  subtext?: string;
}

function StatCard({ label, value, icon, color, subtext }: StatCardProps) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">{label}</p>
          <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
          {subtext && <p className="text-xs text-slate-400 mt-0.5">{subtext}</p>}
        </div>
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${color.replace('text-', 'bg-').replace('-700', '-100').replace('-600', '-100')}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

export function StatsGrid({ stats }: Props) {
  const escalationPct = Math.round(stats.escalation_rate * 100);
  const confidencePct = Math.round(stats.avg_confidence_score * 100);

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        label="Total Conversations"
        value={stats.total_conversations}
        color="text-brand-700"
        icon={
          <svg className="w-5 h-5 text-brand-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
          </svg>
        }
      />
      <StatCard
        label="Escalated"
        value={stats.escalated_conversations}
        color="text-orange-600"
        subtext={`${escalationPct}% of total`}
        icon={
          <svg className="w-5 h-5 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
          </svg>
        }
      />
      <StatCard
        label="Escalation Rate"
        value={`${escalationPct}%`}
        color={escalationPct > 30 ? 'text-red-600' : 'text-emerald-700'}
        subtext={escalationPct > 30 ? 'Above target' : 'Within target'}
        icon={
          <svg className="w-5 h-5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
          </svg>
        }
      />
      <StatCard
        label="Avg Confidence"
        value={`${confidencePct}%`}
        color={confidencePct >= 70 ? 'text-emerald-700' : confidencePct >= 50 ? 'text-amber-600' : 'text-red-600'}
        subtext={confidencePct >= 70 ? 'High quality' : confidencePct >= 50 ? 'Moderate' : 'Low — add more docs'}
        icon={
          <svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        }
      />
    </div>
  );
}
