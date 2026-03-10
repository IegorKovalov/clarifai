import { useRef, useState } from 'react';

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
  isStreaming?: boolean;
}

export function MessageInput({ onSend, disabled, isStreaming }: Props) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled || isStreaming) return;
    onSend(trimmed);
    setValue('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 160) + 'px';
  };

  const canSend = value.trim().length > 0 && !disabled && !isStreaming;

  return (
    <div className="flex items-end gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm focus-within:ring-2 focus-within:ring-brand-500 focus-within:border-transparent transition">
      <textarea
        ref={textareaRef}
        rows={1}
        value={value}
        onChange={handleInput}
        onKeyDown={handleKeyDown}
        placeholder={isStreaming ? 'Waiting for response…' : 'Type a message… (Enter to send)'}
        disabled={disabled || isStreaming}
        className="flex-1 resize-none bg-transparent text-sm text-slate-900 placeholder-slate-400 outline-none disabled:cursor-not-allowed leading-relaxed"
        style={{ maxHeight: '160px' }}
      />
      <button
        onClick={submit}
        disabled={!canSend}
        className="flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center bg-brand-600 hover:bg-brand-700 disabled:opacity-30 disabled:cursor-not-allowed text-white transition"
        aria-label="Send"
      >
        {isStreaming ? (
          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        ) : (
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.269 20.876L5.999 12zm0 0h7.5" />
          </svg>
        )}
      </button>
    </div>
  );
}
