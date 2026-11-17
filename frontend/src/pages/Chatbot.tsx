import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, ShieldCheck, RefreshCw, Info } from 'lucide-react';
import { api } from '../services/api';
import { ChatMessage } from '../types';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge, getAssessmentBadgeVariant } from '../components/ui/badge';
import { formatStatusLabel } from '../lib/utils';

interface ChatbotProps {
  initialPrompt?: string;
  onClearInitialPrompt?: () => void;
  isDemoMode: boolean;
}

const STARTER_PROMPTS = [
  'Explain supervised learning with a practical example.',
  'Compare utilitarian and deontological approaches to an ethical dilemma.',
  'Analyze the privacy implications of collecting biometric data.',
  'Explain the societal effects of AI-driven automation.',
];

export const Chatbot: React.FC<ChatbotProps> = ({
  initialPrompt,
  onClearInitialPrompt,
  isDemoMode,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Welcome to the SafePrompt AI Assistant. Every message is screened for privacy, fairness, and policy alignment prior to generation.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      assessment: 'APPROVED',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (initialPrompt) {
      setInput(initialPrompt);
      if (onClearInitialPrompt) onClearInitialPrompt();
    }
  }, [initialPrompt, onClearInitialPrompt]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (textOverride?: string) => {
    const query = (textOverride ?? input).trim();
    if (!query || loading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const resp = await api.chat(query);
      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: resp.reply,
        assessment: resp.assessment as any,
        safety_notes: `${resp.model_name} · ${resp.latency_ms} ms`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `Unable to reach the backend service: ${err.message}.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-[26px] font-semibold tracking-tight text-[#0F172A] leading-tight">
            AI Assistant
          </h1>
          <p className="text-[14px] text-[#64748B] mt-1">
            Policy-gated conversational interface with pre-generation screening and safe fallback handling.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => setMessages([messages[0]])}
        >
          <RefreshCw className="h-3.5 w-3.5" />
          New Conversation
        </Button>
      </div>

      {/* Chat Shell */}
      <Card className="flex flex-col h-[calc(100vh-14rem)] min-h-[480px] overflow-hidden">
        {/* Top Guardrail Status Bar */}
        <div className="flex items-center justify-between border-b border-[#E2E8F0] bg-[#F8FAFC] px-5 py-3 text-[12px]">
          <div className="flex items-center gap-2 text-[#475569]">
            <ShieldCheck className="h-4 w-4 text-[#059669]" />
            <span className="font-medium text-[#0F172A]">Pre-generation guardrails active</span>
          </div>

          <Badge variant={isDemoMode ? 'warning' : 'success'}>
            {isDemoMode ? 'Offline Demo Responses' : 'Gemini Live API'}
          </Badge>
        </div>

        {/* Unobtrusive Demo Mode Notice */}
        {isDemoMode && (
          <div className="flex items-center gap-2 border-b border-amber-200/70 bg-amber-50/60 px-5 py-2 text-[12px] text-amber-900">
            <Info className="h-3.5 w-3.5 text-[#D97706] shrink-0" />
            <span>
              Demo mode is active because no external API key is configured. Responses are predefined local demonstrations, not live model outputs.
            </span>
          </div>
        )}

        {/* Messages Feed */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5 bg-white">
          {messages.map((msg) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={msg.id}
                className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
              >
                <div
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border ${
                    isUser
                      ? 'bg-[#2563EB] border-[#2563EB] text-white'
                      : 'bg-[#F8FAFC] border-[#E2E8F0] text-[#475569]'
                  }`}
                >
                  {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>

                <div className={`max-w-[78%] space-y-1.5 ${isUser ? 'items-end flex flex-col' : ''}`}>
                  <div
                    className={`rounded-xl px-4 py-3 text-[14px] leading-relaxed whitespace-pre-wrap ${
                      isUser
                        ? 'bg-[#2563EB] text-white'
                        : msg.assessment === 'BLOCKED' || msg.assessment === 'NOT_APPROVED'
                        ? 'bg-red-50/70 border border-red-200 text-red-950'
                        : 'bg-[#F8FAFC] border border-[#E2E8F0] text-[#0F172A]'
                    }`}
                  >
                    {msg.content}
                  </div>

                  <div className="flex flex-wrap items-center gap-2 px-1 text-[11px] text-[#64748B]">
                    <span>{msg.timestamp}</span>
                    {msg.assessment && !isUser && (
                      <Badge variant={getAssessmentBadgeVariant(msg.assessment)}>
                        {formatStatusLabel(msg.assessment)}
                      </Badge>
                    )}
                    {msg.safety_notes && (
                      <span className="truncate max-w-sm text-[#94A3B8]">{msg.safety_notes}</span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] text-[#475569]">
                <Bot className="h-4 w-4" />
              </div>
              <div className="rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] px-4 py-2.5 text-[13px] text-[#64748B]">
                Checking prompt policies and generating response...
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Starter Prompts + Input Composer */}
        <div className="border-t border-[#E2E8F0] bg-[#F8FAFC] p-4 space-y-3">
          <div className="flex flex-wrap gap-1.5">
            {STARTER_PROMPTS.map((starter) => (
              <button
                key={starter}
                onClick={() => handleSend(starter)}
                disabled={loading}
                className="rounded-lg border border-[#E2E8F0] bg-white px-2.5 py-1 text-[12px] text-[#475569] hover:border-[#2563EB]/40 hover:text-[#2563EB] transition-colors truncate max-w-xs"
              >
                {starter}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Write a message..."
              className="h-10 flex-1 rounded-lg border border-[#E2E8F0] bg-white px-3.5 text-[14px] text-[#0F172A] placeholder-[#94A3B8] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB]/15"
            />
            <Button onClick={() => handleSend()} disabled={loading || !input.trim()} size="lg">
              <Send className="h-4 w-4" />
              Send
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};
