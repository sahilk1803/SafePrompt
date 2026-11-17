import React, { useEffect, useState } from 'react';
import {
  Download,
  Search,
  CheckCircle2,
  Shield,
  Info
} from 'lucide-react';
import { api } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge, getAssessmentBadgeVariant } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { formatStatusLabel, formatDateTime } from '../lib/utils';

const GOVERNANCE_CHECKLIST = [
  {
    pillar: 'Human Oversight',
    desc: 'Review workflow enables manual approval or correction for ambiguous decisions.',
  },
  {
    pillar: 'Privacy & Data Governance',
    desc: 'Raw prompts are excluded from routine logs; SHA-256 hashes and sanitized previews are retained.',
  },
  {
    pillar: 'Fairness & Inclusion',
    desc: 'Rule-based fairness checks flag discriminatory criteria prior to model execution.',
  },
  {
    pillar: 'Transparency',
    desc: 'Every policy decision surfaces plain-language rationale, categories, and risk scores.',
  },
  {
    pillar: 'Reliability',
    desc: 'Instruction boundary checks isolate user-supplied data from system instructions.',
  },
  {
    pillar: 'Social & Environmental Well-Being',
    desc: 'Impact scenarios and documented sustainability assumptions inform responsible deployment.',
  },
  {
    pillar: 'Accountability',
    desc: 'Timestamped SQLite audit records track assessment outcomes and versioned policies.',
  },
];

export const GovernanceAudit: React.FC = () => {
  const [records, setRecords] = useState<any[]>([]);
  const [notice, setNotice] = useState('');
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [reviewedIds, setReviewedIds] = useState<Record<string, boolean>>({});
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    api.getAudit(50).then((data) => {
      setRecords(data.records || []);
      setNotice(data.data_minimization_notice || '');
    });
  }, []);

  const filtered = records.filter((r) => {
    const q = search.trim().toLowerCase();
    const matchesSearch =
      !q || r.id.toLowerCase().includes(q) || (r.snippet || '').toLowerCase().includes(q);
    const matchesStatus =
      filterStatus === 'ALL' ||
      r.assessment === filterStatus ||
      (filterStatus === 'BLOCKED' && r.assessment === 'NOT_APPROVED');
    return matchesSearch && matchesStatus;
  });

  const handleExportCsv = () => {
    const headers = ['Analysis_ID', 'Timestamp', 'Prompt_Hash', 'Status', 'Risk_Score', 'Policy_Version'];
    const rows = filtered.map((r) => [
      r.id,
      r.timestamp,
      r.prompt_hash,
      formatStatusLabel(r.assessment),
      r.risk_score,
      r.policy_version,
    ]);
    const csv = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'safeprompt_audit_logs.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleReviewApprove = async (analysisId: string) => {
    await api.submitReview(
      analysisId,
      'workspace_reviewer',
      'APPROVED',
      'Reviewed and confirmed via Audit Logs.'
    );
    setReviewedIds((prev) => ({ ...prev, [analysisId]: true }));
    setToast(`Review recorded for ${analysisId}`);
    setTimeout(() => setToast(null), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[26px] font-semibold tracking-tight text-[#0F172A] leading-tight">
            Audit Logs
          </h1>
          <p className="text-[14px] text-[#64748B] mt-1">
            Inspect data-minimized governance records, complete human reviews, and export sanitized reports.
          </p>
        </div>

        <Button variant="outline" onClick={handleExportCsv}>
          <Download className="h-4 w-4" />
          Export CSV
        </Button>
      </div>

      {notice && (
        <Alert variant="info">
          <Shield className="h-4 w-4 text-[#2563EB] shrink-0 mt-0.5" />
          <AlertDescription>{notice}</AlertDescription>
        </Alert>
      )}

      {toast && (
        <Alert variant="success">
          <CheckCircle2 className="h-4 w-4 text-[#059669] shrink-0 mt-0.5" />
          <AlertDescription>{toast}</AlertDescription>
        </Alert>
      )}

      {/* Audit Records Table */}
      <Card>
        <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 space-y-0 pb-4">
          <div>
            <CardTitle>Analysis Records ({filtered.length})</CardTitle>
            <CardDescription>Sanitized prompt metadata stored in SQLite</CardDescription>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="h-3.5 w-3.5 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search ID or preview..."
                className="h-8 w-52 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] pl-8 pr-3 text-[12px] text-[#0F172A] placeholder-[#94A3B8] outline-none focus:border-[#2563EB] focus:bg-white"
              />
            </div>

            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="h-8 rounded-lg border border-[#E2E8F0] bg-white px-2.5 text-[12px] text-[#0F172A] outline-none focus:border-[#2563EB]"
            >
              <option value="ALL">All Statuses</option>
              <option value="APPROVED">Approved</option>
              <option value="CAUTION">Caution</option>
              <option value="NEEDS_REVIEW">Review</option>
              <option value="BLOCKED">Blocked</option>
            </select>
          </div>
        </CardHeader>

        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-[13px]">
              <thead>
                <tr className="border-y border-[#E2E8F0] bg-[#F8FAFC] text-[12px] font-medium text-[#64748B]">
                  <th className="py-3 px-5">Analysis ID</th>
                  <th className="py-3 px-4">Fingerprint</th>
                  <th className="py-3 px-4">Prompt Preview</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Risk Score</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-5 text-right">Review</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9]">
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-10 text-center text-[#64748B]">
                      No matching audit logs found.
                    </td>
                  </tr>
                ) : (
                  filtered.map((rec) => {
                    const isReviewed = reviewedIds[rec.id];
                    return (
                      <tr key={rec.id} className="hover:bg-[#F8FAFC] transition-colors">
                        <td className="py-3.5 px-5 font-mono text-[12px] font-medium text-[#0F172A] whitespace-nowrap">
                          {rec.id}
                        </td>
                        <td className="py-3.5 px-4 font-mono text-[12px] text-[#64748B] whitespace-nowrap">
                          {rec.prompt_hash}
                        </td>
                        <td className="py-3.5 px-4 text-[#334155] max-w-xs truncate">
                          {rec.snippet}
                        </td>
                        <td className="py-3.5 px-4 whitespace-nowrap">
                          <Badge variant={getAssessmentBadgeVariant(rec.assessment)}>
                            {formatStatusLabel(rec.assessment)}
                          </Badge>
                        </td>
                        <td className="py-3.5 px-4 text-right font-mono text-[12px] text-[#0F172A]">
                          {rec.risk_score}
                        </td>
                        <td className="py-3.5 px-4 text-[12px] text-[#64748B] whitespace-nowrap">
                          {formatDateTime(rec.timestamp)}
                        </td>
                        <td className="py-3.5 px-5 text-right whitespace-nowrap">
                          {isReviewed ? (
                            <Badge variant="success">Reviewed</Badge>
                          ) : (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleReviewApprove(rec.id)}
                            >
                              Approve
                            </Button>
                          )}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Governance Checklist */}
      <Card>
        <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 space-y-0 pb-4">
          <div>
            <CardTitle>Responsible AI Governance Checklist</CardTitle>
            <CardDescription>
              Framework reference aligned with NIST AI RMF and Trustworthy AI principles
            </CardDescription>
          </div>
          <span className="inline-flex items-center gap-1.5 text-[12px] text-[#64748B]">
            <Info className="h-3.5 w-3.5" />
            Informational checklist — not legal certification
          </span>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {GOVERNANCE_CHECKLIST.map((item) => (
              <div
                key={item.pillar}
                className="flex items-start gap-3 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] p-3.5"
              >
                <CheckCircle2 className="h-4 w-4 text-[#059669] shrink-0 mt-0.5" />
                <div>
                  <div className="text-[13px] font-semibold text-[#0F172A]">{item.pillar}</div>
                  <p className="text-[12px] text-[#64748B] mt-1 leading-relaxed">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
