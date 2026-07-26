import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardOverview } from './pages/DashboardOverview';
import { DigitalTwinPage } from './pages/DigitalTwinPage';
import { ScansPage } from './pages/ScansPage';
import { VulnerabilitiesPage } from './pages/VulnerabilitiesPage';
import { AttackPathsPage } from './pages/AttackPathsPage';
import { ThreatIntelPage } from './pages/ThreatIntelPage';
import { ReportsPage } from './pages/ReportsPage';
import { IntegrationsPage } from './pages/IntegrationsPage';
import { SettingsPage } from './pages/SettingsPage';
import { NewScanModal } from './components/NewScanModal';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [isScanModalOpen, setIsScanModalOpen] = useState<boolean>(false);

  const renderActivePage = () => {
    switch (activeTab) {
      case 'overview':
        return <DashboardOverview onOpenScanModal={() => setIsScanModalOpen(true)} />;
      case 'digital-twin':
        return <DigitalTwinPage />;
      case 'scans':
        return <ScansPage onOpenScanModal={() => setIsScanModalOpen(true)} />;
      case 'vulnerabilities':
        return <VulnerabilitiesPage />;
      case 'attack-paths':
        return <AttackPathsPage />;
      case 'threat-intel':
        return <ThreatIntelPage />;
      case 'reports':
        return <ReportsPage />;
      case 'integrations':
        return <IntegrationsPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <DashboardOverview onOpenScanModal={() => setIsScanModalOpen(true)} />;
    }
  };

  return (
    <div className="app-container">
      {/* Left Navigation Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main App Content Area */}
      <div className="main-content">
        <Header onOpenScanModal={() => setIsScanModalOpen(true)} />
        {renderActivePage()}
      </div>

      {/* Interactive Scan Modal */}
      <NewScanModal
        isOpen={isScanModalOpen}
        onClose={() => setIsScanModalOpen(false)}
      />
    </div>
  );
};
