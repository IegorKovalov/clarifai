export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  confidence?: number;
  escalated?: boolean;
  streaming?: boolean;
  decision?: string;
}

export interface WsTokenEvent {
  type: 'token';
  content: string;
}

export interface WsDoneEvent {
  type: 'done';
  confidence: number;
  escalated: boolean;
  session_id: string;
  generation?: string;
  decision?: string;
}

export interface WsErrorEvent {
  type: 'error';
  content: string;
}

export type WsEvent = WsTokenEvent | WsDoneEvent | WsErrorEvent;

export interface AdminStats {
  total_conversations: number;
  escalated_conversations: number;
  escalation_rate: number;
  avg_confidence_score: number;
}

export interface IngestResponse {
  document_id: string;
  status: string;
  message: string;
}

export interface TenantInfo {
  id: string;
  name: string;
  api_key: string;
  escalation_email: string | null;
  bot_name: string;
  is_active: boolean;
  created_at: string;
}
