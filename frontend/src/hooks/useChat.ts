import { useCallback, useEffect, useRef, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { buildWsUrl } from '../services/api';
import type { Message, WsEvent } from '../types';

type ChatStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

interface UseChatReturn {
  messages: Message[];
  status: ChatStatus;
  isStreaming: boolean;
  isThinking: boolean;
  sessionId: string;
  sendMessage: (text: string) => void;
  resetSession: () => void;
  error: string | null;
}

export function useChat(apiKey: string): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [status, setStatus] = useState<ChatStatus>('disconnected');
  const [isStreaming, setIsStreaming] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState(() => uuidv4());

  const wsRef = useRef<WebSocket | null>(null);
  const streamingIdRef = useRef<string | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (!apiKey) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setStatus('connecting');
    setError(null);

    const ws = new WebSocket(buildWsUrl(apiKey, sessionId));
    wsRef.current = ws;

    ws.onopen = () => setStatus('connected');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data) as WsEvent;

      if (data.type === 'token') {
        setIsThinking(false);
        setIsStreaming(true);
        // Ensure the streaming ID is set before the setState closure captures it
        if (!streamingIdRef.current) {
          streamingIdRef.current = uuidv4();
        }
        const currentId = streamingIdRef.current;
        setMessages((prev) => {
          const exists = prev.some((m) => m.id === currentId);
          if (!exists) {
            return [
              ...prev,
              {
                id: currentId,
                role: 'assistant',
                content: data.content,
                timestamp: new Date(),
                streaming: true,
              },
            ];
          }
          return prev.map((m) =>
            m.id === currentId ? { ...m, content: m.content + data.content } : m,
          );
        });
      }

      if (data.type === 'done') {
        setIsThinking(false);
        setIsStreaming(false);

        const finishedId = streamingIdRef.current;
        streamingIdRef.current = null;

        if (finishedId) {
          // Capture values before the async setState closure runs
          const { confidence, escalated, decision } = data;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === finishedId
                ? { ...m, streaming: false, confidence, escalated, decision }
                : m,
            ),
          );
        } else if (data.generation) {
          // No tokens were streamed (off_topic / escalate path) — create bubble from generation
          setMessages((prev) => [
            ...prev,
            {
              id: uuidv4(),
              role: 'assistant',
              content: data.generation!,
              timestamp: new Date(),
              confidence: data.confidence,
              escalated: data.escalated,
              decision: data.decision,
              streaming: false,
            },
          ]);
        }
      }

      if (data.type === 'error') {
        setIsThinking(false);
        setIsStreaming(false);
        streamingIdRef.current = null;
        setError(data.content);
        setMessages((prev) => [
          ...prev,
          {
            id: uuidv4(),
            role: 'assistant',
            content: `⚠️ ${data.content}`,
            timestamp: new Date(),
          },
        ]);
      }
    };

    ws.onclose = (e) => {
      setStatus('disconnected');
      setIsStreaming(false);
      // Auth failure — don't retry
      if (e.code === 1008) {
        setError('Invalid API key. Please check your key and try again.');
        return;
      }
      // Auto-reconnect after 2s for other disconnects
      if (apiKey) {
        reconnectTimeoutRef.current = setTimeout(connect, 2000);
      }
    };

    ws.onerror = () => {
      setStatus('error');
      setError('Connection failed. Retrying...');
    };
  }, [apiKey, sessionId]);

  useEffect(() => {
    if (apiKey) {
      connect();
    }
    return () => {
      reconnectTimeoutRef.current && clearTimeout(reconnectTimeoutRef.current);
      wsRef.current?.close();
    };
  }, [apiKey, sessionId]);

  const sendMessage = useCallback(
    (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isStreaming) return;
      if (wsRef.current?.readyState !== WebSocket.OPEN) {
        setError('Not connected. Please wait...');
        return;
      }

      setError(null);
      setIsThinking(true);
      const userMsg: Message = {
        id: uuidv4(),
        role: 'user',
        content: trimmed,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
      wsRef.current.send(JSON.stringify({ message: trimmed }));
    },
    [isStreaming],
  );

  const resetSession = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setMessages([]);
    setError(null);
    setIsStreaming(false);
    setIsThinking(false);
    streamingIdRef.current = null;
    setSessionId(uuidv4());
  }, []);

  return { messages, status, isStreaming, isThinking, sessionId, sendMessage, resetSession, error };
}
