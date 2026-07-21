import React from 'react';
import { SecurityScoreGauge } from '../components/SecurityScoreGauge';
import { MetricCard } from '../components/MetricCard';
import { DigitalTwinGraph } from '../components/DigitalTwinGraph';
import { AttackTimeline } from '../components/AttackTimeline';
import { RiskRadarChart } from '../components/RiskRadarChart';
import { VulnerabilitiesList } from '../components/VulnerabilitiesList';
import { ScanStatusCard } from '../components/ScanStatusCard';

interface DashboardOverviewProps {
  onOpenScanModal: () => void;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({ onOpenScanModal }) => {
  return (
    <div className="page-container">
      <div className="dashboard-grid">
        {/* Top Row: Metric Cards (3 cols each = 12 cols total) */}
        <SecurityScoreGauge score={72} />
        
        <MetricCard
          title="Critical Vulnerabilities"
          value={6}
          changeText="↑ 2 from last scan"
          isIncrease={true}
          trendColor="red"
          sparklineData={[3, 4, 3, 5, 4, 6]}
        />

        <MetricCard
          title="Total Assets Mapped"
          value={128}
          changeText="↑ 18 new"
          isIncrease={true}
          trendColor="blue"
          sparklineData={[90, 95, 104, 110, 115, 128]}
        />

        <MetricCard
          title="Attacks Detected"
          value={347}
          changeText="↓ 12%"
          isIncrease={false}
          trendColor="green"
          sparklineData={[420, 390, 410, 370, 350, 347]}
        />

        {/* Middle Row: Digital Twin Graph (7 cols) + Attack Timeline (5 cols) */}
        <DigitalTwinGraph />
        <AttackTimeline />

        {/* Bottom Row: Risk Radar (4 cols) + Vulnerabilities (4 cols) + Scan Status (4 cols) */}
        <RiskRadarChart />
        <VulnerabilitiesList />
        <ScanStatusCard onOpenScanModal={onOpenScanModal} />
      </div>
    </div>
  );
};
