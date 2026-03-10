import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../../types';

interface Props {
  message: Message;
}

function ConfidencePill({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 80 ? 'bg-emerald-100 text-emerald-700' :
    pct >= 50 ? 'bg-amber-100 text-amber-700' :
    'bg-red-100 text-red-600';
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full ${color}`}>
      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
      </svg>
      {pct}% confidence
    </span>
  );
}

function EscalationPill() {
  return (
    <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full bg-orange-100 text-orange-700">
      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
      </svg>
      Escalated to support
    </span>
  );
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 animate-slide-up ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold shadow-sm ${
        isUser
          ? 'bg-brand-600 text-white'
          : 'bg-slate-200 text-slate-600'
      }`}>
        {isUser ? 'U' : 'AI'}
      </div>

      <div className={`flex flex-col gap-1.5 max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? 'bg-brand-600 text-white rounded-tr-sm'
            : 'bg-white text-slate-800 border border-slate-200 rounded-tl-sm shadow-sm'
        }`}>
          {isUser ? (
            <p className="whitespace-pre-wrap break-words">{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none prose-slate
              prose-p:my-1 prose-p:leading-relaxed
              prose-headings:text-slate-800 prose-headings:font-semibold prose-headings:mt-3 prose-headings:mb-1
              prose-strong:text-slate-900 prose-strong:font-semibold
              prose-ul:my-1 prose-ul:pl-4 prose-li:my-0.5
              prose-ol:my-1 prose-ol:pl-4
              prose-code:text-brand-700 prose-code:bg-brand-50 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-xs prose-code:font-mono
              prose-table:text-xs prose-table:border-collapse
              prose-th:bg-slate-100 prose-th:px-3 prose-th:py-1.5 prose-th:text-left prose-th:font-semibold prose-th:border prose-th:border-slate-200
              prose-td:px-3 prose-td:py-1.5 prose-td:border prose-td:border-slate-200
              prose-a:text-brand-600 prose-a:underline
              prose-blockquote:border-l-brand-300 prose-blockquote:text-slate-600">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Meta row */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-[11px] text-slate-400">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
          {!message.streaming && message.decision === 'vectorstore' && message.confidence !== undefined && (
            <ConfidencePill score={message.confidence} />
          )}
          {!message.streaming && message.escalated && <EscalationPill />}
        </div>
      </div>
    </div>
  );
}
