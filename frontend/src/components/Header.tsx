import React, { useState, useRef, useEffect } from 'react';
import { Bell, Settings, Menu, ChevronRight } from 'lucide-react';
import { DashboardResponse } from '../types';
import { formatStatusLabel, formatDateTime } from '../lib/utils';

interface HeaderProps {
  sectionLabel: string;
  pageTitle: string;
  isDemoMode: boolean;
  isConnected: boolean;
  semanticAvailable?: boolean;
  semanticStatus?: string;
  recentActivity?: DashboardResponse['recent_activity'];
  onOpenSettings: () => void;
  onOpenMobileMenu: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  sectionLabel,
  pageTitle,
  isDemoMode,
  isConnected,
  semanticAvailable = false,
  semanticStatus = 'unconfigured_demo',
  recentActivity = [],
  onOpenSettings,
  onOpenMobileMenu,
}) => {
  const [notifOpen, setNotifOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setNotifOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const flaggedItems = recentActivity.filter((r) => r.assessment !== 'APPROVED').slice(0, 4);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-[#E2E8F0] bg-[#FFFFFF] px-4 lg:px-8 shrink-0">
      {/* Left: Mobile toggle + Breadcrumb + Page Title */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={onOpenMobileMenu}
          className="lg:hidden inline-flex h-9 w-9 items-center justify-center rounded-lg border border-[#E2E8F0] text-[#475569] hover:bg-slate-50"
          aria-label="Open navigation menu"
        >
          <Menu className="h-4 w-4" />
        </button>

        <div className="flex items-center gap-1.5 text-[13px] min-w-0">
          <span className="hidden sm:inline text-[#64748B] font-normal">{sectionLabel}</span>
          <ChevronRight className="hidden sm:inline h-3.5 w-3.5 text-[#CBD5E1] shrink-0" />
          <span className="font-semibold text-[#0F172A] truncate text-[14px]">{pageTitle}</span>
        </div>
      </div>

      {/* Right: Connection Status, Notifications, Settings, Avatar */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Verified Semantic / Local Connection Indicator */}
        <div
          className="flex items-center gap-2 rounded-full border border-[#E2E8F0] bg-[#F8FAFC] px-3 py-1 text-[12px] text-[#475569]"
          title={
            !isConnected
              ? 'Backend service is unreachable'
              : semanticAvailable
              ? 'Verified live Gemini semantic classification + local policy rules active'
              : semanticStatus === 'unconfigured_demo'
              ? 'Running local policy rules only (no Gemini API key configured — reduced semantic coverage)'
              : 'Semantic AI classifier unavailable — running local fallback policy rules with reduced semantic coverage'
          }
        >
          <span
            className={`h-2 w-2 rounded-full ${
              !isConnected
                ? 'bg-[#DC2626]'
                : semanticAvailable
                ? 'bg-[#059669]'
                : 'bg-[#D97706]'
            }`}
          />
          <span className="font-medium text-[#0F172A]">
            {!isConnected
              ? 'Offline'
              : semanticAvailable
              ? 'Hybrid AI Active'
              : 'Local Rules Only'}
          </span>
          {isConnected && !semanticAvailable && (
            <span className="border-l border-[#E2E8F0] pl-2 text-[11px] font-medium text-[#64748B]">
              {isDemoMode ? 'Demo' : 'Fallback'}
            </span>
          )}
        </div>

        {/* Notifications */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setNotifOpen((prev) => !prev)}
            className="relative inline-flex h-9 w-9 items-center justify-center rounded-lg text-[#64748B] hover:bg-slate-100 hover:text-[#0F172A] transition-colors"
            aria-label="Notifications"
          >
            <Bell className="h-4 w-4" strokeWidth={1.75} />
            {flaggedItems.length > 0 && (
              <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-[#2563EB]" />
            )}
          </button>

          {notifOpen && (
            <div className="absolute right-0 mt-2 w-80 rounded-xl border border-[#E2E8F0] bg-white shadow-lg py-2 z-50">
              <div className="px-4 py-2 border-b border-[#E2E8F0] flex items-center justify-between">
                <span className="text-[13px] font-semibold text-[#0F172A]">Recent Alerts</span>
                <span className="text-[11px] text-[#64748B]">{flaggedItems.length} flagged</span>
              </div>
              {flaggedItems.length === 0 ? (
                <div className="px-4 py-6 text-center text-[13px] text-[#64748B]">
                  No recent flagged prompts.
                </div>
              ) : (
                <div className="divide-y divide-[#F1F5F9]">
                  {flaggedItems.map((item) => (
                    <div key={item.id} className="px-4 py-2.5 hover:bg-slate-50 transition-colors">
                      <div className="flex items-center justify-between text-[12px]">
                        <span className="font-mono font-medium text-[#0F172A]">{item.id}</span>
                        <span className="text-[11px] text-[#64748B]">{formatDateTime(item.timestamp)}</span>
                      </div>
                      <p className="text-[12px] text-[#64748B] truncate mt-0.5">{item.snippet}</p>
                      <span className="inline-block mt-1 text-[11px] font-medium text-[#D97706]">
                        {formatStatusLabel(item.assessment)} · Risk {item.risk_score}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Settings Shortcut */}
        <button
          onClick={onOpenSettings}
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg text-[#64748B] hover:bg-slate-100 hover:text-[#0F172A] transition-colors"
          aria-label="Settings"
          title="Settings"
        >
          <Settings className="h-4 w-4" strokeWidth={1.75} />
        </button>

        {/* User Avatar */}
        <button
          onClick={onOpenSettings}
          className="ml-1 flex h-8 w-8 items-center justify-center rounded-full bg-[#2563EB] text-[12px] font-semibold text-white hover:bg-[#1D4ED8] transition-colors"
          title="Workspace Profile"
        >
          AD
        </button>
      </div>
    </header>
  );
};
