import React, { useEffect, useState } from 'react';
import { Leaf, Zap, Droplets, Cloud, Info, Activity } from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer
} from 'recharts';
import { api } from '../services/api';
import { SustainabilityMetrics } from '../types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Alert, AlertTitle, AlertDescription } from '../components/ui/alert';

const REGIONS = [
  'India (National Avg)',
  'Global Average',
  'US Average',
  'EU Average',
  'Green / Renewable Datacenter',
];

export const GreenAIDashboard: React.FC = () => {
  const [region, setRegion] = useState('India (National Avg)');
  const [data, setData] = useState<SustainabilityMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getSustainability(region).then((res) => {
      setData(res);
      setLoading(false);
    });
  }, [region]);

  if (loading || !data) {
    return (
      <div className="space-y-4">
        <div className="h-10 w-64 rounded-lg bg-slate-200/70 animate-pulse" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 rounded-xl bg-white border border-[#E2E8F0] animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[26px] font-semibold tracking-tight text-[#0F172A] leading-tight">
            Sustainability
          </h1>
          <p className="text-[14px] text-[#64748B] mt-1">
            Track request volume, estimated token counts, and modeled computational resource consumption.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-[12px] font-medium text-[#64748B]">Grid Region:</label>
          <select
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            className="h-9 rounded-lg border border-[#E2E8F0] bg-white px-3 text-[13px] font-medium text-[#0F172A] shadow-sm outline-none focus:border-[#2563EB]"
          >
            {REGIONS.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Explicit Estimation Disclaimer */}
      <Alert variant="warning">
        <Info className="h-4 w-4 text-[#D97706] shrink-0 mt-0.5" />
        <div>
          <AlertTitle>Estimation Assumptions</AlertTitle>
          <AlertDescription>{data.assumptions_disclaimer}</AlertDescription>
        </div>
      </Alert>

      {/* 4 Resource KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-[13px] font-medium text-[#64748B]">Tracked Requests</span>
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50">
                <Activity className="h-4 w-4 text-[#2563EB]" />
              </div>
            </div>
            <div className="mt-3 text-[28px] font-semibold text-[#0F172A] leading-none">
              {data.total_requests}
            </div>
            <p className="mt-2 text-[12px] text-[#64748B] font-mono">
              ~{data.estimated_tokens.toLocaleString()} est. tokens
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-[13px] font-medium text-[#64748B]">Est. Energy</span>
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-50">
                <Zap className="h-4 w-4 text-[#D97706]" />
              </div>
            </div>
            <div className="mt-3 text-[28px] font-semibold text-[#0F172A] leading-none">
              {data.estimated_energy_kwh} <span className="text-[14px] font-normal text-[#64748B]">kWh</span>
            </div>
            <p className="mt-2 text-[12px] text-[#64748B] font-mono">PUE 1.18 assumption</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-[13px] font-medium text-[#64748B]">Est. Emissions</span>
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50">
                <Cloud className="h-4 w-4 text-[#059669]" />
              </div>
            </div>
            <div className="mt-3 text-[28px] font-semibold text-[#0F172A] leading-none">
              {data.estimated_carbon_gco2e} <span className="text-[14px] font-normal text-[#64748B]">gCO2e</span>
            </div>
            <p className="mt-2 text-[12px] text-[#64748B] font-mono">
              {data.grid_intensity} gCO2/kWh grid factor
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <div className="flex items-center justify-between">
              <span className="text-[13px] font-medium text-[#64748B]">Est. Cooling Water</span>
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-50">
                <Droplets className="h-4 w-4 text-[#0284C7]" />
              </div>
            </div>
            <div className="mt-3 text-[28px] font-semibold text-[#0F172A] leading-none">
              {data.estimated_water_ml} <span className="text-[14px] font-normal text-[#64748B]">mL</span>
            </div>
            <p className="mt-2 text-[12px] text-[#64748B] font-mono">~1.25 mL / request</p>
          </CardContent>
        </Card>
      </div>

      {/* Model Energy Chart */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle>Modeled Energy Usage</CardTitle>
          <CardDescription>Estimated Watt-hours (Wh) across tracked request intervals</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.historical_usage} margin={{ top: 10, right: 12, left: -16, bottom: 0 }}>
                <defs>
                  <linearGradient id="energyFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#059669" stopOpacity={0.16} />
                    <stop offset="95%" stopColor="#059669" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                <XAxis dataKey="hour" stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94A3B8" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    border: '1px solid #E2E8F0',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(15,23,42,0.08)',
                    fontSize: '12px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="energy_wh"
                  name="Energy (Wh)"
                  stroke="#059669"
                  strokeWidth={2}
                  fill="url(#energyFill)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Efficient Prompting Guidance */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Leaf className="h-4 w-4 text-[#059669]" />
            Sustainable Prompt Engineering Practices
          </CardTitle>
          <CardDescription>Strategies for lowering computational overhead</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {data.green_tips.map((tip) => (
              <div
                key={tip.title}
                className="rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] p-4 space-y-1.5"
              >
                <div className="text-[13px] font-semibold text-[#0F172A]">{tip.title}</div>
                <p className="text-[12px] text-[#64748B] leading-relaxed">{tip.text}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
