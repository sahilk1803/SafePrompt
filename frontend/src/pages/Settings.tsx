import React, { useEffect, useState } from 'react';
import {
  Server,
  Shield,
  Database,
  CheckCircle2,
  KeyRound,
  ChevronDown,
  ChevronUp,
  BookOpen
} from 'lucide-react';
import { api } from '../services/api';
import { DashboardResponse } from '../types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';

interface SettingsProps {
  isDemoMode: boolean;
  isConnected: boolean;
  dashboardData: DashboardResponse | null;
}

export const Settings: React.FC<SettingsProps> = ({
  isDemoMode,
  isConnected,
  dashboardData,
}) => {
  const [health, setHealth] = useState<{
    status: string;
    app: string;
    version: string;
    demo_mode: boolean;
    active_model?: string;
    semantic_classifier_available?: boolean;
    semantic_status?: string;
    analysis_mode_default?: string;
  } | null>(null);
  const [defaultRedactionMode, setDefaultRedactionMode] = useState('placeholder');
  const [requirePiiConfirm, setRequirePiiConfirm] = useState(true);
  const [strictBoundaryMode, setStrictBoundaryMode] = useState(true);
  const [savedNotice, setSavedNotice] = useState(false);

  // Optional collapsible reference mapping (preserves internal curriculum mapping cleanly)
  const [showReference, setShowReference] = useState(false);
  const [referenceUnits, setReferenceUnits] = useState<any[]>([]);

  useEffect(() => {
    api.getHealth().then(setHealth).catch(() => null);
  }, []);

  const handleToggleReference = () => {
    if (!showReference && referenceUnits.length === 0) {
      api.getSyllabus().then((res) => setReferenceUnits(res.units || [])).catch(() => null);
    }
    setShowReference((prev) => !prev);
  };

  const handlePreferenceChange = (setter: (v: any) => void, val: any) => {
    setter(val);
    setSavedNotice(true);
    setTimeout(() => setSavedNotice(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Page Header */}
      <div>
        <h1 className="text-[26px] font-semibold tracking-tight text-[#0F172A] leading-tight">
          Settings
        </h1>
        <p className="text-[14px] text-[#64748B] mt-1">
          Manage AI provider status, policy configuration, privacy controls, and system diagnostics.
        </p>
      </div>

      {savedNotice && (
        <Alert variant="success">
          <CheckCircle2 className="h-4 w-4 text-[#059669] shrink-0 mt-0.5" />
          <AlertDescription>Workspace preferences updated for this session.</AlertDescription>
        </Alert>
      )}

      {/* AI Provider & Connection Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-4 w-4 text-[#2563EB]" />
            AI Provider &amp; Runtime Status
          </CardTitle>
          <CardDescription>
            Live connection health and model configuration
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-[13px]">
            <div className="rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] p-3.5">
              <div className="text-[12px] text-[#64748B] mb-1">Backend API Status</div>
              <div className="flex items-center justify-between">
                <span className="font-semibold text-[#0F172A]">
                  {isConnected ? 'Operational' : 'Disconnected'}
                </span>
                <Badge variant={isConnected ? 'success' : 'error'}>
                  {isConnected ? 'Connected' : 'Offline'}
                </Badge>
              </div>
            </div>

            <div className="rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] p-3.5">
              <div className="text-[12px] text-[#64748B] mb-1">Semantic Classifier Mode</div>
              <div className="flex items-center justify-between">
                <span className="font-semibold text-[#0F172A]">
                  {health?.semantic_classifier_available
                    ? 'Hybrid (Rules + Gemini)'
                    : isDemoMode
                    ? 'Local Demo Fallback'
                    : 'Local Fallback (Unverified)'}
                </span>
                <Badge variant={health?.semantic_classifier_available ? 'success' : 'warning'}>
                  {health?.semantic_classifier_available ? 'Verified Live' : 'Local Only'}
                </Badge>
              </div>
            </div>

            <div className="rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] p-3.5">
              <div className="text-[12px] text-[#64748B] mb-1">Active Model</div>
              <div className="font-mono text-[13px] font-medium text-[#0F172A]">
                {health?.active_model || (isDemoMode ? 'local-demo-simulator' : 'gemini-3.5-flash-lite')}
              </div>
            </div>

            <div className="rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] p-3.5">
              <div className="text-[12px] text-[#64748B] mb-1">Application Version</div>
              <div className="font-mono text-[13px] font-medium text-[#0F172A]">
                v{health?.version || '1.0.0'}
              </div>
            </div>
          </div>

          <Alert variant="default">
            <KeyRound className="h-4 w-4 text-[#64748B] shrink-0 mt-0.5" />
            <AlertDescription className="text-[#475569]">
              API credentials are managed exclusively server-side via the <code className="text-[12px] bg-slate-200/70 px-1.5 py-0.5 rounded">GEMINI_API_KEY</code> environment variable and are never exposed to the browser.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Policy & Privacy Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-[#2563EB]" />
            Policy &amp; Guardrail Preferences
          </CardTitle>
          <CardDescription>
            Active enforcement policy and default redaction behavior
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between py-2 border-b border-[#F1F5F9]">
            <div>
              <div className="text-[14px] font-medium text-[#0F172A]">Active Policy Version</div>
              <div className="text-[12px] text-[#64748B]">Deterministic rulebook applied during prompt analysis</div>
            </div>
            <Badge variant="outline" className="font-mono">2026.2-v2.0</Badge>
          </div>

          <div className="flex items-center justify-between py-2 border-b border-[#F1F5F9]">
            <div>
              <div className="text-[14px] font-medium text-[#0F172A]">Default Redaction Format</div>
              <div className="text-[12px] text-[#64748B]">Format applied when masking personal identifiers</div>
            </div>
            <select
              value={defaultRedactionMode}
              onChange={(e) => handlePreferenceChange(setDefaultRedactionMode, e.target.value)}
              className="h-9 rounded-lg border border-[#E2E8F0] bg-white px-3 text-[13px] text-[#0F172A] outline-none focus:border-[#2563EB]"
            >
              <option value="placeholder">Placeholder ([EMAIL_1])</option>
              <option value="mask">Labeled Mask ([REDACTED: EMAIL])</option>
              <option value="hash">Strict Redact ([REDACTED])</option>
            </select>
          </div>

          <div className="flex items-center justify-between py-2 border-b border-[#F1F5F9]">
            <div>
              <div className="text-[14px] font-medium text-[#0F172A]">Require Confirmation Before PII Egress</div>
              <div className="text-[12px] text-[#64748B]">Prevent forwarding unmasked identifiers to external models</div>
            </div>
            <input
              type="checkbox"
              checked={requirePiiConfirm}
              onChange={(e) => handlePreferenceChange(setRequirePiiConfirm, e.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-[#2563EB] focus:ring-[#2563EB]"
            />
          </div>

          <div className="flex items-center justify-between py-2">
            <div>
              <div className="text-[14px] font-medium text-[#0F172A]">Strict Instruction Boundary Checks</div>
              <div className="text-[12px] text-[#64748B]">Flag formatting or persona conflict directives in user prompts</div>
            </div>
            <input
              type="checkbox"
              checked={strictBoundaryMode}
              onChange={(e) => handlePreferenceChange(setStrictBoundaryMode, e.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-[#2563EB] focus:ring-[#2563EB]"
            />
          </div>
        </CardContent>
      </Card>

      {/* Storage & System Diagnostics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-4 w-4 text-[#2563EB]" />
            Storage &amp; Telemetry
          </CardTitle>
          <CardDescription>Local SQLite database status and runtime stack</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-[13px]">
            <div className="rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] p-3.5">
              <div className="text-[12px] text-[#64748B]">Database Engine</div>
              <div className="font-semibold text-[#0F172A] mt-0.5">SQLite (Local)</div>
            </div>
            <div className="rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] p-3.5">
              <div className="text-[12px] text-[#64748B]">Audit Records Stored</div>
              <div className="font-semibold text-[#0F172A] mt-0.5 font-mono">
                {dashboardData?.total_prompts ?? 0} analyses
              </div>
            </div>
            <div className="rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] p-3.5">
              <div className="text-[12px] text-[#64748B]">Runtime Stack</div>
              <div className="font-semibold text-[#0F172A] mt-0.5">FastAPI · React · SQLite</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Optional Collapsible Reference Mapping */}
      <Card>
        <button
          type="button"
          onClick={handleToggleReference}
          className="flex w-full items-center justify-between p-5 text-left hover:bg-[#F8FAFC] transition-colors rounded-xl"
        >
          <div className="flex items-center gap-2.5">
            <BookOpen className="h-4 w-4 text-[#64748B]" />
            <div>
              <div className="text-[14px] font-semibold text-[#0F172A]">
                Framework Documentation &amp; Capability Mapping
              </div>
              <div className="text-[12px] text-[#64748B]">
                Optional reference overview of implemented safety, ethics, governance, and sustainability modules
              </div>
            </div>
          </div>
          {showReference ? (
            <ChevronUp className="h-4 w-4 text-[#64748B]" />
          ) : (
            <ChevronDown className="h-4 w-4 text-[#64748B]" />
          )}
        </button>

        {showReference && (
          <CardContent className="border-t border-[#E2E8F0] pt-4 space-y-3">
            {referenceUnits.map((item, idx) => (
              <div
                key={idx}
                className="rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] p-3.5 text-[13px]"
              >
                <div className="font-semibold text-[#0F172A]">{item.title}</div>
                <p className="text-[12px] text-[#64748B] mt-1">{item.implementation}</p>
              </div>
            ))}
          </CardContent>
        )}
      </Card>
    </div>
  );
};
