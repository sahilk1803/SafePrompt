import React, { useState, useEffect, useMemo } from 'react';
import {
  Activity,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  ArrowRight,
  ScanText,
  ShieldCheck,
  FileText,
  Search,
  Calendar,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { DashboardResponse, SustainabilityMetrics } from '../types';
import { api } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge, getAssessmentBadgeVariant } from '../components/ui/badge';
import { formatStatusLabel, formatCategoryLabel, formatDateTime } from '../lib/utils';

interface DashboardProps {
  data: DashboardResponse | null;
  loading: boolean;
  onNavigate: (tab: string) => void;
}

const DONUT_COLORS: Record<string, string> = {
  Approved: '#059669',
  Caution: '#D97706',
  Review: '#2563EB',
  Blocked: '#DC2626',
};

const PAGE_SIZE = 5;

export const Dashboard: React.FC<DashboardProps> = ({ data, loading, onNavigate }) => {
  const [dateRange, setDateRange] = useState<'all' | '7d' | 'today'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [currentPage, setCurrentPage] = useState(1);
  const [activitySeries, setActivitySeries] = useState<Array<{ hour: string; requests: number }>>([]);
  const [auditRecords, setAuditRecords] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([
      api.getSustainability().catch(() => null),
      api.getAudit(50).catch(() => null),
    ]).then(([sust, audit]) => {
      if (sust && (sust as SustainabilityMetrics).historical_usage) {
        setActivitySeries((sust as SustainabilityMetrics).historical_usage);
      }
      if (audit && audit.records) {
        setAuditRecords(audit.records);
      }
    });
  }, [data?.total_prompts]);

  const tableSource = useMemo(() => {
    const raw = auditRecords.length > 0 ? auditRecords : data?.recent_activity || [];
    const now = Date.now();
    return raw.filter((item) => {
      if (dateRange === 'today') {
        const ts = new Date(item.timestamp).getTime();
        if (!Number.isNaN(ts) && now - ts > 24 * 60 * 60 * 1000) return false;
      } else if (dateRange === '7d') {
        const ts = new Date(item.timestamp).getTime();
        if (!Number.isNaN(ts) && now - ts > 7 * 24 * 60 * 60 * 1000) return false;
      }

      const matchesStatus =
        statusFilter === 'ALL' ||
        item.assessment === statusFilter ||
        (statusFilter === 'BLOCKED' && item.assessment === 'NOT_APPROVED');
      const q = searchQuery.trim().toLowerCase();
      const matchesSearch =
        !q ||
        item.id.toLowerCase().includes(q) ||
        (item.snippet || '').toLowerCase().includes(q);
      return matchesStatus && matchesSearch;
    });
  }, [auditRecords, data?.recent_activity, dateRange, statusFilter, searchQuery]);

  const totalPages = Math.max(1, Math.ceil(tableSource.length / PAGE_SIZE));
  const paginatedRows = tableSource.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, statusFilter, dateRange]);

  if (loading || !data) {
    return (
      <div className="space-y-6">
        <div className="h-12 w-64 rounded-lg bg-slate-200/70 animate-pulse" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 rounded-xl bg-white border border-[#E2E8F0] animate-pulse" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-72 rounded-xl bg-white border border-[#E2E8F0] animate-pulse" />
          <div className="h-72 rounded-xl bg-white border border-[#E2E8F0] animate-pulse" />
        </div>
      </div>
    );
  }

  const flaggedTotal = data.caution_count + data.needs_review_count + data.not_approved_count;

  const donutData = [
    { name: 'Approved', value: data.approved_count },
    { name: 'Caution', value: data.caution_count },
    { name: 'Review', value: data.needs_review_count },
    { name: 'Blocked', value: data.not_approved_count },
  ].filter((d) => d.value > 0);

  const statCards = [
    {
      label: 'Total Prompts Analyzed',
      value: data.total_prompts,
      sub: `Avg. ${data.avg_latency_ms} ms response`,
      icon: Activity,
      iconColor: 'text-[#2563EB]',
      iconBg: 'bg-blue-50',
    },
    {
      label: 'Approved Requests',
      value: data.approved_count,
      sub: data.total_prompts > 0 ? `${Math.round((data.approved_count / data.total_prompts) * 100)}% of total` : 'No requests yet',
      icon: CheckCircle2,
      iconColor: 'text-[#059669]',
      iconBg: 'bg-emerald-50',
    },
    {
      label: 'Requests Flagged',
      value: flaggedTotal,
      sub: `${data.not_approved_count} blocked · ${data.caution_count} caution`,
      icon: AlertTriangle,
      iconColor: 'text-[#D97706]',
      iconBg: 'bg-amber-50',
    },
    {
      label: 'Privacy Issues Detected',
      value: data.pii_detections,
      sub: 'Pre-submission PII checks',
      icon: ShieldAlert,
      iconColor: 'text-[#DC2626]',
      iconBg: 'bg-red-50',
    },
  ];

  const quickActions = [
    {
      title: 'Analyze a Prompt',
      description: 'Inspect risk categories, policy alignment, and suggested improvements.',
      icon: ScanText,
      tab: 'analyzer',
    },
    {
      title: 'Protect Sensitive Data',
      description: 'Detect and mask emails, phone numbers, credentials, and IDs locally.',
      icon: ShieldCheck,
      tab: 'privacy',
    },
    {
      title: 'Review AI Activity',
      description: 'Audit minimized prompt logs, review outcomes, and export reports.',
      icon: FileText,
      tab: 'governance',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[26px] font-semibold tracking-tight text-[#0F172A] leading-tight">
            Overview
          </h1>
          <p className="text-[14px] text-[#64748B] mt-1">
            Monitor prompt activity, safety insights, and responsible AI performance.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="relative flex items-center">
            <Calendar className="h-4 w-4 text-[#64748B] absolute left-3 pointer-events-none" />
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value as any)}
              className="h-9 rounded-lg border border-[#E2E8F0] bg-white pl-9 pr-8 text-[13px] font-medium text-[#0F172A] shadow-sm outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB]/15"
              aria-label="Date range filter"
            >
              <option value="all">All Time</option>
              <option value="7d">Last 7 Days</option>
              <option value="today">Last 24 Hours</option>
            </select>
          </div>

          <Button onClick={() => onNavigate('analyzer')}>
            Analyze Prompt
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* 4 Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className="transition-shadow hover:shadow-card-hover">
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <span className="text-[13px] font-medium text-[#64748B]">{stat.label}</span>
                  <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${stat.iconBg}`}>
                    <Icon className={`h-4 w-4 ${stat.iconColor}`} strokeWidth={1.75} />
                  </div>
                </div>
                <div className="mt-3 text-[28px] font-semibold tracking-tight text-[#0F172A] leading-none">
                  {stat.value}
                </div>
                <p className="mt-2 text-[12px] text-[#64748B]">{stat.sub}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Analytics Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Prompt Activity Line/Area Chart */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle>Prompt Activity</CardTitle>
            <CardDescription>Analyzed requests recorded across recent intervals</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={activitySeries} margin={{ top: 10, right: 12, left: -16, bottom: 0 }}>
                  <defs>
                    <linearGradient id="promptActivityFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563EB" stopOpacity={0.14} />
                      <stop offset="95%" stopColor="#2563EB" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                  <XAxis
                    dataKey="hour"
                    stroke="#94A3B8"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    stroke="#94A3B8"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    allowDecimals={false}
                  />
                  <RechartsTooltip
                    contentStyle={{
                      backgroundColor: '#FFFFFF',
                      border: '1px solid #E2E8F0',
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(15,23,42,0.08)',
                      fontSize: '12px',
                      color: '#0F172A',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="requests"
                    name="Requests"
                    stroke="#2563EB"
                    strokeWidth={2}
                    fill="url(#promptActivityFill)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Risk Distribution Donut Chart */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle>Risk Distribution</CardTitle>
            <CardDescription>Policy decisions across analyzed prompts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-52 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={donutData}
                    cx="50%"
                    cy="50%"
                    innerRadius={56}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                    stroke="none"
                  >
                    {donutData.map((entry) => (
                      <Cell key={entry.name} fill={DONUT_COLORS[entry.name] || '#64748B'} />
                    ))}
                  </Pie>
                  <RechartsTooltip
                    contentStyle={{
                      backgroundColor: '#FFFFFF',
                      border: '1px solid #E2E8F0',
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(15,23,42,0.08)',
                      fontSize: '12px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 grid grid-cols-2 gap-2 pt-2 border-t border-[#F1F5F9]">
              {['Approved', 'Caution', 'Review', 'Blocked'].map((label) => {
                const count =
                  label === 'Approved'
                    ? data.approved_count
                    : label === 'Caution'
                    ? data.caution_count
                    : label === 'Review'
                    ? data.needs_review_count
                    : data.not_approved_count;
                return (
                  <div key={label} className="flex items-center justify-between text-[12px] px-1">
                    <span className="flex items-center gap-1.5 text-[#64748B]">
                      <span
                        className="h-2 w-2 rounded-full"
                        style={{ backgroundColor: DONUT_COLORS[label] }}
                      />
                      {label}
                    </span>
                    <span className="font-semibold text-[#0F172A]">{count}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {quickActions.map((action) => {
          const Icon = action.icon;
          return (
            <button
              key={action.title}
              onClick={() => onNavigate(action.tab)}
              className="group text-left rounded-xl border border-[#E2E8F0] bg-white p-5 shadow-card transition-all hover:border-[#2563EB]/40 hover:shadow-card-hover"
            >
              <div className="flex items-center justify-between">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#EFF6FF] text-[#2563EB]">
                  <Icon className="h-4 w-4" strokeWidth={1.75} />
                </div>
                <ArrowRight className="h-4 w-4 text-[#94A3B8] transition-transform group-hover:translate-x-0.5 group-hover:text-[#2563EB]" />
              </div>
              <div className="mt-3 text-[14px] font-semibold text-[#0F172A]">{action.title}</div>
              <p className="mt-1 text-[13px] text-[#64748B] leading-snug">{action.description}</p>
            </button>
          );
        })}
      </div>

      {/* Recent Activity Table */}
      <Card>
        <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 space-y-0 pb-4">
          <div>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Minimized prompt analysis records from the database</CardDescription>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="h-3.5 w-3.5 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search ID or preview..."
                className="h-8 w-48 rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] pl-8 pr-3 text-[12px] text-[#0F172A] placeholder-[#94A3B8] outline-none focus:border-[#2563EB] focus:bg-white"
              />
            </div>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
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
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-y border-[#E2E8F0] bg-[#F8FAFC] text-[12px] font-medium text-[#64748B]">
                  <th className="py-3 px-5">Analysis ID</th>
                  <th className="py-3 px-4">Prompt Preview</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Risk Score</th>
                  <th className="py-3 px-5 text-right">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9] text-[13px]">
                {paginatedRows.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-10 text-center text-[#64748B]">
                      No matching prompt analyses found.
                    </td>
                  </tr>
                ) : (
                  paginatedRows.map((row) => {
                    const primaryCat =
                      Array.isArray(row.categories) && row.categories.length > 0
                        ? formatCategoryLabel(row.categories[0])
                        : 'General';
                    return (
                      <tr key={row.id} className="hover:bg-[#F8FAFC] transition-colors">
                        <td className="py-3.5 px-5 font-mono text-[12px] font-medium text-[#0F172A] whitespace-nowrap">
                          {row.id}
                        </td>
                        <td className="py-3.5 px-4 text-[#334155] max-w-xs truncate">
                          {row.snippet}
                        </td>
                        <td className="py-3.5 px-4 whitespace-nowrap">
                          <Badge variant="outline">{primaryCat}</Badge>
                        </td>
                        <td className="py-3.5 px-4 whitespace-nowrap">
                          <Badge variant={getAssessmentBadgeVariant(row.assessment)}>
                            {formatStatusLabel(row.assessment)}
                          </Badge>
                        </td>
                        <td className="py-3.5 px-4 text-right font-mono text-[12px] text-[#0F172A] whitespace-nowrap">
                          {row.risk_score} / 100
                        </td>
                        <td className="py-3.5 px-5 text-right text-[12px] text-[#64748B] whitespace-nowrap">
                          {formatDateTime(row.timestamp)}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div className="flex items-center justify-between border-t border-[#E2E8F0] px-5 py-3 text-[12px] text-[#64748B]">
            <span>
              Showing {tableSource.length === 0 ? 0 : (currentPage - 1) * PAGE_SIZE + 1}–
              {Math.min(currentPage * PAGE_SIZE, tableSource.length)} of {tableSource.length} records
            </span>
            <div className="flex items-center gap-1.5">
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage <= 1}
                onClick={() => setCurrentPage((p) => p - 1)}
              >
                <ChevronLeft className="h-3.5 w-3.5" />
                Prev
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={currentPage >= totalPages}
                onClick={() => setCurrentPage((p) => p + 1)}
              >
                Next
                <ChevronRight className="h-3.5 w-3.5" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
