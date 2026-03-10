import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { ApiKeyGate } from '../components/shared/ApiKeyGate';
import { MessageBubble } from '../components/chat/MessageBubble';
import { MessageInput } from '../components/chat/MessageInput';
import { StatusBadge } from '../components/shared/StatusBadge';
import { useChat } from '../hooks/useChat';
import { submitFeedback } from '../services/api';

const STORAGE_KEY = 'clarifai_api_key';

export default function ChatPage() {
  const [apiKey, setApiKey] = useState(() => localStorage.getItem(STORAGE_KEY) ?? '');
  const [feedbackSent, setFeedbackSent] = useState<Set<string>>(new Set());
  const bottomRef = useRef<HTMLDivElement>(null);

  const { messages, status, isStreaming, isThinking, sessionId, sendMessage, resetSession, error } =
    useChat(apiKey);

  const handleApiKey = (key: string) => {
    localStorage.setItem(STORAGE_KEY, key);
    setApiKey(key);
  };

  const handleLogout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setApiKey('');
    resetSession();
  };

  const handleFeedback = async (msgId: string, feedback: 'thumbs_up' | 'thumbs_down') => {
    if (feedbackSent.has(msgId)) return;
    try {
      await submitFeedback(apiKey, sessionId, feedback);
      setFeedbackSent((prev) => new Set([...prev, msgId]));
    } catch {
      // silently ignore
    }
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!apiKey) {
    return (
      <ApiKeyGate
        onSubmit={handleApiKey}
        title="Customer Support Chat"
        description="Enter your API key to start chatting with our AI assistant."
      />
    );
  }

  const lastAssistantMsg = [...messages].reverse().find(
    (m) => m.role === 'assistant' && !m.streaming && m.decision === 'vectorstore'
  );

  return (
    <div className="flex flex-col h-screen bg-slate-50">
      {/* Header */}
      <header className="flex-shrink-0 flex items-center justify-between px-4 sm:px-6 py-3.5 bg-white border-b border-slate-200 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center shadow">
            <svg className="w-4.5 h-4.5 text-white w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
            </svg>
          </div>
          <div>
            <h1 className="text-sm font-semibold text-slate-900 leading-none">ClarifAI Support</h1>
            <StatusBadge status={status} />
          </div>
        </div>

        <div className="flex items-center gap-1">
          <Link
            to="/admin"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-brand-600 px-2.5 py-1.5 rounded-lg hover:bg-slate-100 transition"
            title="Admin dashboard"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
            </svg>
            Admin
          </Link>
          <button
            onClick={resetSession}
            title="New conversation"
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
            </svg>
          </button>
          <button
            onClick={handleLogout}
            title="Logout"
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
            </svg>
          </button>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto scrollbar-thin px-4 sm:px-6 py-6 space-y-5">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-3 animate-fade-in">
            <div className="w-14 h-14 rounded-2xl bg-brand-100 flex items-center justify-center">
              <svg className="w-7 h-7 text-brand-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-700">How can I help you today?</p>
              <p className="text-xs text-slate-400 mt-1">Ask me anything about your account or our services.</p>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id}>
            <MessageBubble message={msg} />
            {/* Feedback buttons only for RAG answers */}
            {msg.role === 'assistant' && !msg.streaming && msg.decision === 'vectorstore' && msg.id === lastAssistantMsg?.id && (
              <div className="flex items-center gap-2 mt-1.5 ml-11">
                <span className="text-xs text-slate-400">Helpful?</span>
                {feedbackSent.has(msg.id) ? (
                  <span className="text-xs text-slate-400 italic">Thanks for your feedback!</span>
                ) : (
                  <>
                    <button
                      onClick={() => handleFeedback(msg.id, 'thumbs_up')}
                      className="text-slate-400 hover:text-emerald-600 transition text-sm"
                      title="Thumbs up"
                    >
                      👍
                    </button>
                    <button
                      onClick={() => handleFeedback(msg.id, 'thumbs_down')}
                      className="text-slate-400 hover:text-red-500 transition text-sm"
                      title="Thumbs down"
                    >
                      👎
                    </button>
                  </>
                )}
              </div>
            )}
          </div>
        ))}

        {/* Thinking indicator — shows between send and first token */}
        {isThinking && (
          <div className="flex gap-3 animate-fade-in">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-xs font-semibold text-slate-600">
              AI
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-sm shadow-sm px-4 py-3.5 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.3s]" />
              <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.15s]" />
              <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" />
            </div>
          </div>
        )}

        {error && (
          <div className="flex justify-center animate-fade-in">
            <div className="inline-flex items-center gap-2 bg-red-50 text-red-600 text-xs px-3 py-2 rounded-lg border border-red-200">
              <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
              </svg>
              {error}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 px-4 sm:px-6 pb-5 pt-3 bg-white border-t border-slate-100">
        <MessageInput onSend={sendMessage} isStreaming={isStreaming || isThinking} disabled={status !== 'connected'} />
        <p className="text-center text-[11px] text-slate-400 mt-2">
          Session: <span className="font-mono">{sessionId.slice(0, 8)}…</span>
        </p>
      </div>
    </div>
  );
}
