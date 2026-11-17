import React from 'react';
import {
  LayoutGrid,
  ScanText,
  ShieldCheck,
  MessageSquare,
  Lock,
  FileText,
  Leaf,
  Settings,
  Shield,
  PanelLeftClose,
  PanelLeftOpen,
  X
} from 'lucide-react';
import { cn } from '../lib/utils';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  collapsed: boolean;
  setCollapsed: (val: boolean) => void;
  mobileOpen: boolean;
  setMobileOpen: (val: boolean) => void;
}

const NAV_GROUPS = [
  {
    label: 'Workspace',
    items: [
      { id: 'dashboard', label: 'Overview', icon: LayoutGrid },
      { id: 'analyzer', label: 'Prompt Analyzer', icon: ScanText },
      { id: 'privacy', label: 'Privacy Protection', icon: ShieldCheck },
      { id: 'chatbot', label: 'AI Assistant', icon: MessageSquare },
    ],
  },
  {
    label: 'Monitoring',
    items: [
      { id: 'integrity', label: 'Security Insights', icon: Lock },
      { id: 'governance', label: 'Audit Logs', icon: FileText },
      { id: 'greenai', label: 'Sustainability', icon: Leaf },
    ],
  },
  {
    label: 'System',
    items: [
      { id: 'settings', label: 'Settings', icon: Settings },
    ],
  },
];

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  collapsed,
  setCollapsed,
  mobileOpen,
  setMobileOpen,
}) => {
  const handleSelect = (id: string) => {
    setActiveTab(id);
    setMobileOpen(false);
  };

  const sidebarContent = (
    <div className="flex h-full flex-col bg-[#FFFFFF] border-r border-[#E2E8F0] select-none">
      {/* Brand Header */}
      <div
        className={cn(
          'flex h-16 items-center border-b border-[#E2E8F0] px-4 shrink-0',
          collapsed ? 'justify-center px-2' : 'justify-between'
        )}
      >
        <button
          onClick={() => handleSelect('dashboard')}
          className="flex items-center gap-2.5 text-left focus:outline-none"
        >
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#2563EB] text-white shadow-sm">
            <Shield className="h-4 w-4" strokeWidth={2.2} />
          </div>
          {!collapsed && (
            <div className="leading-tight">
              <div className="text-[15px] font-semibold tracking-tight text-[#0F172A]">
                SafePrompt
              </div>
              <div className="text-[11px] font-normal text-[#64748B]">
                Responsible AI Platform
              </div>
            </div>
          )}
        </button>

        {!collapsed && (
          <button
            onClick={() => setCollapsed(true)}
            title="Collapse sidebar"
            className="hidden lg:inline-flex h-7 w-7 items-center justify-center rounded-md text-[#64748B] hover:bg-slate-100 hover:text-[#0F172A] transition-colors"
          >
            <PanelLeftClose className="h-4 w-4" strokeWidth={1.75} />
          </button>
        )}

        <button
          onClick={() => setMobileOpen(false)}
          className="lg:hidden inline-flex h-7 w-7 items-center justify-center rounded-md text-[#64748B] hover:bg-slate-100 hover:text-[#0F172A]"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Navigation Groups */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
        {NAV_GROUPS.map((group) => (
          <div key={group.label}>
            {!collapsed && (
              <div className="px-2.5 pb-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#94A3B8]">
                {group.label}
              </div>
            )}
            <div className="space-y-0.5">
              {group.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleSelect(item.id)}
                    title={collapsed ? item.label : undefined}
                    className={cn(
                      'group relative flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-[14px] font-medium transition-colors',
                      collapsed && 'justify-center px-0',
                      isActive
                        ? 'bg-[#EFF6FF] text-[#2563EB]'
                        : 'text-[#475569] hover:bg-slate-100/80 hover:text-[#0F172A]'
                    )}
                  >
                    {isActive && (
                      <span className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r-full bg-[#2563EB]" />
                    )}
                    <Icon
                      className={cn(
                        'h-4 w-4 shrink-0 transition-colors',
                        isActive ? 'text-[#2563EB]' : 'text-[#64748B] group-hover:text-[#0F172A]'
                      )}
                      strokeWidth={1.75}
                    />
                    {!collapsed && <span className="truncate">{item.label}</span>}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Bottom Workspace / User Section */}
      <div className="border-t border-[#E2E8F0] p-3 shrink-0">
        {collapsed ? (
          <button
            onClick={() => setCollapsed(false)}
            title="Expand sidebar"
            className="flex h-9 w-full items-center justify-center rounded-lg text-[#64748B] hover:bg-slate-100 hover:text-[#0F172A] transition-colors"
          >
            <PanelLeftOpen className="h-4 w-4" strokeWidth={1.75} />
          </button>
        ) : (
          <div className="flex items-center justify-between rounded-lg px-2 py-1.5 hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-100 border border-[#E2E8F0] text-[12px] font-semibold text-[#0F172A]">
                SP
              </div>
              <div className="min-w-0 leading-tight">
                <div className="truncate text-[13px] font-medium text-[#0F172A]">
                  Default Workspace
                </div>
                <div className="truncate text-[11px] text-[#64748B]">
                  Standard Governance
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside
        className={cn(
          'hidden lg:block shrink-0 transition-all duration-200',
          collapsed ? 'w-[68px]' : 'w-[250px]'
        )}
      >
        {sidebarContent}
      </aside>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div
            className="fixed inset-0 bg-slate-900/30 backdrop-blur-[1px]"
            onClick={() => setMobileOpen(false)}
          />
          <div className="relative z-10 w-[260px] max-w-[80vw] h-full shadow-xl">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
};
