import React, { useState } from 'react';
import { ShieldCheck, EyeOff, Copy, Check, ArrowRight, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import { RedactResponse } from '../types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';

interface PrivacyShieldProps {
  onUseSanitized?: (sanitizedText: string) => void;
}

const SYNTHETIC_SAMPLES = [
  {
    id: 'contact',
    label: 'Contact information (Email & Phone)',
    text: 'Hello Dr. Mehta, my email is alex.rivera@example.com and my phone number is +91-98765-43210. Please share the meeting agenda.',
  },
  {
    id: 'credentials',
    label: 'Infrastructure credentials & IP',
    text: 'Please debug our database connection at 192.168.1.45 using my temporary API token sk-abcdef1234567890abcdef1234567890abcdef12.',
  },
  {
    id: 'ids',
    label: 'National ID & Payment card',
    text: 'My test national ID number is 2345 6789 0123 and my synthetic payment card is 4111111111111111 for checkout testing.',
  },
];

export const PrivacyShield: React.FC<PrivacyShieldProps> = ({ onUseSanitized }) => {
  const [inputText, setInputText] = useState(SYNTHETIC_SAMPLES[0].text);
  const [selectedSample, setSelectedSample] = useState('contact');
  const [mode, setMode] = useState<'placeholder' | 'mask' | 'hash'>('placeholder');
  const [result, setResult] = useState<RedactResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleSampleChange = (id: string) => {
    setSelectedSample(id);
    const found = SYNTHETIC_SAMPLES.find((s) => s.id === id);
    if (found) {
      setInputText(found.text);
      setResult(null);
    }
  };

  const handleScan = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    try {
      const data = await api.redactPii(inputText, mode);
      setResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (result?.sanitized_text) {
      navigator.clipboard.writeText(result.sanitized_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-[26px] font-semibold tracking-tight text-[#0F172A] leading-tight">
          Privacy Protection
        </h1>
        <p className="text-[14px] text-[#64748B] mt-1">
          Detect and redact personally identifiable information locally before sending prompts to external AI providers.
        </p>
      </div>

      {/* Main Redaction Workspace */}
      <Card>
        <CardHeader className="flex flex-col md:flex-row md:items-center justify-between gap-4 space-y-0 border-b border-[#E2E8F0] pb-4">
          <div className="flex flex-wrap items-center gap-3">
            <div>
              <label className="block text-[11px] font-medium uppercase tracking-wider text-[#64748B] mb-1">
                Synthetic Example
              </label>
              <select
                value={selectedSample}
                onChange={(e) => handleSampleChange(e.target.value)}
                className="h-9 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] px-3 text-[13px] text-[#0F172A] outline-none focus:border-[#2563EB] focus:bg-white"
              >
                {SYNTHETIC_SAMPLES.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-medium uppercase tracking-wider text-[#64748B] mb-1">
                Masking Format
              </label>
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value as any)}
                className="h-9 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] px-3 text-[13px] text-[#0F172A] outline-none focus:border-[#2563EB] focus:bg-white"
              >
                <option value="placeholder">Placeholder ([EMAIL_1])</option>
                <option value="mask">Labeled Mask ([REDACTED: EMAIL])</option>
                <option value="hash">Strict Redact ([REDACTED])</option>
              </select>
            </div>
          </div>

          <div className="flex items-end">
            <Button onClick={handleScan} disabled={loading || !inputText.trim()}>
              <EyeOff className="h-4 w-4" />
              {loading ? 'Scanning...' : 'Scan & Redact'}
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-5 space-y-5">
          {/* Side-by-Side Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-[12px] font-semibold text-[#475569]">
                  Original Text (Local Only)
                </label>
                <span className="text-[12px] text-[#94A3B8] font-mono">
                  {inputText.length} chars
                </span>
              </div>
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                rows={7}
                className="w-full rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] p-4 text-[14px] text-[#0F172A] outline-none focus:border-[#2563EB] focus:bg-white resize-none leading-relaxed"
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-[12px] font-semibold text-[#059669] flex items-center gap-1.5">
                  <ShieldCheck className="h-3.5 w-3.5" />
                  Sanitized Text (Safe for External Model)
                </label>
                {result && (
                  <Badge variant={result.detected_count > 0 ? 'success' : 'secondary'}>
                    {result.detected_count} masked
                  </Badge>
                )}
              </div>
              <div className="h-[188px] w-full rounded-xl border border-[#E2E8F0] bg-white p-4 font-mono text-[13px] text-[#0F172A] overflow-y-auto leading-relaxed">
                {result ? (
                  result.sanitized_text
                ) : (
                  <span className="font-sans text-[#94A3B8]">
                    Run &ldquo;Scan &amp; Redact&rdquo; to preview sanitized text before transmission.
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Action Footer */}
          {result && (
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-[#F1F5F9]">
              <span className="text-[12px] text-[#64748B]">
                Personal identifiers are not transmitted externally without explicit confirmation.
              </span>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={handleCopy}>
                  {copied ? <Check className="h-3.5 w-3.5 text-[#059669]" /> : <Copy className="h-3.5 w-3.5" />}
                  {copied ? 'Copied' : 'Copy Sanitized Text'}
                </Button>
                {onUseSanitized && (
                  <Button size="sm" onClick={() => onUseSanitized(result.sanitized_text)}>
                    Use Sanitized Text
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Detected Entities Mapping */}
      {result && result.findings.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle>Detected Identifiers</CardTitle>
            <CardDescription>
              Mapping between redacted placeholders and masked previews
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-[13px]">
                <thead>
                  <tr className="border-y border-[#E2E8F0] bg-[#F8FAFC] text-[12px] font-medium text-[#64748B]">
                    <th className="py-2.5 px-4">Placeholder</th>
                    <th className="py-2.5 px-4">Entity Type</th>
                    <th className="py-2.5 px-4">Severity</th>
                    <th className="py-2.5 px-4">Masked Preview</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9]">
                  {result.findings.map((finding, i) => {
                    const mapEntries = Object.entries(result.entity_map);
                    const entry = mapEntries[i];
                    return (
                      <tr key={i} className="hover:bg-[#F8FAFC]">
                        <td className="py-3 px-4 font-mono text-[12px] font-semibold text-[#2563EB]">
                          {entry ? entry[0] : `[${finding.entity_type.toUpperCase()}]`}
                        </td>
                        <td className="py-3 px-4 text-[#0F172A]">{finding.label}</td>
                        <td className="py-3 px-4">
                          <Badge
                            variant={
                              finding.severity === 'critical' || finding.severity === 'high'
                                ? 'error'
                                : 'warning'
                            }
                          >
                            {finding.severity}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 font-mono text-[12px] text-[#64748B]">
                          {entry ? entry[1] : '****'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <Alert variant="default">
              <AlertCircle className="h-4 w-4 text-[#64748B] shrink-0 mt-0.5" />
              <AlertDescription className="text-[#64748B]">
                Automated pattern matching detects structured identifiers rapidly, but manual review is recommended for unstructured personal details.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
