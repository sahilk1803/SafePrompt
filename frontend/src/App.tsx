import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { Analyzer } from './pages/Analyzer';
import { PrivacyShield } from './pages/PrivacyShield';
import { Chatbot } from './pages/Chatbot';
import { InstructionIntegrity } from './pages/InstructionIntegrity';
import { GovernanceAudit } from './pages/GovernanceAudit';
import { GreenAIDashboard } from './pages/GreenAIDashboard';
import { Settings } from './pages/Settings';
import { api } from './services/api';
import { DashboardResponse } from './types';

const ROUTE_META: Record<string, { section: string; title: string }> = {
  dashboard: { section: 'Workspace', title: 'Overview' },
  analyzer: { section: 'Workspace', title: 'Prompt Analyzer' },
  privacy: { section: 'Workspace', title: 'Privacy Protection' },
  chatbot: { section: 'Workspace', title: 'AI Assistant' },
  integrity: { section: 'Monitoring', title: 'Security Insights' },
  governance: { section: 'Monitoring', title: 'Audit Logs' },
  greenai: { section: 'Monitoring', title: 'Sustainability' },
  settings: { section: 'System', title: 'Settings' },
};

export function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null);
  const [loadingDash, setLoadingDash] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState(true);
  const [isConnected, setIsConnected] = useState(true);
  const [semanticAvailable, setSemanticAvailable] = useState(false);
  const [semanticStatus, setSemanticStatus] = useState<string>('unconfigured_demo');
  const [queuedChatPrompt, setQueuedChatPrompt] = useState<string>('');

  const fetchDashboard = useCallback(async () => {
    try {
      const [dash, health] = await Promise.all([api.getDashboard(), api.getHealth()]);
      setDashboardData(dash);
      setIsDemoMode(health.demo_mode);
      setSemanticAvailable(Boolean(health.semantic_classifier_available));
      setSemanticStatus(health.semantic_status || (health.demo_mode ? 'unconfigured_demo' : 'unavailable_local_fallback'));
      setIsConnected(true);
    } catch (e) {
      console.error('Failed to connect to SafePrompt API:', e);
      setIsConnected(false);
      setSemanticAvailable(false);
      setSemanticStatus('unavailable_local_fallback');
    } finally {
      setLoadingDash(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  const handleUsePromptInChat = (promptText: string) => {
    setQueuedChatPrompt(promptText);
    setActiveTab('chatbot');
  };

  const currentMeta = ROUTE_META[activeTab] || { section: 'Workspace', title: 'Overview' };

  return (
    <div className="flex h-screen bg-[#F8FAFC] text-[#0F172A] overflow-hidden">
      {/* Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
        mobileOpen={mobileMenuOpen}
        setMobileOpen={setMobileMenuOpen}
      />

      {/* Main Content Shell */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header
          sectionLabel={currentMeta.section}
          pageTitle={currentMeta.title}
          isDemoMode={isDemoMode}
          isConnected={isConnected}
          semanticAvailable={semanticAvailable}
          semanticStatus={semanticStatus}
          recentActivity={dashboardData?.recent_activity || []}
          onOpenSettings={() => setActiveTab('settings')}
          onOpenMobileMenu={() => setMobileMenuOpen(true)}
        />

        <main className="flex-1 overflow-y-auto px-4 py-6 lg:px-8 lg:py-8">
          <div className="mx-auto max-w-[1280px]">
            {activeTab === 'dashboard' && (
              <Dashboard
                data={dashboardData}
                loading={loadingDash}
                onNavigate={setActiveTab}
              />
            )}

            {activeTab === 'analyzer' && (
              <Analyzer
                onAnalysisComplete={fetchDashboard}
                onUsePromptInChat={handleUsePromptInChat}
              />
            )}

            {activeTab === 'privacy' && (
              <PrivacyShield onUseSanitized={handleUsePromptInChat} />
            )}

            {activeTab === 'chatbot' && (
              <Chatbot
                initialPrompt={queuedChatPrompt}
                onClearInitialPrompt={() => setQueuedChatPrompt('')}
                isDemoMode={isDemoMode}
              />
            )}

            {activeTab === 'integrity' && <InstructionIntegrity />}

            {activeTab === 'governance' && <GovernanceAudit />}

            {activeTab === 'greenai' && <GreenAIDashboard />}

            {activeTab === 'settings' && (
              <Settings
                isDemoMode={isDemoMode}
                isConnected={isConnected}
                dashboardData={dashboardData}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
