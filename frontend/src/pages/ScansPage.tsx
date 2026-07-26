import React from 'react';
import { Radar, Play, CheckCircle2, AlertOctagon, Clock, ExternalLink } from 'lucide-react';

interface ScansPageProps {
  onOpenScanModal: () => void;
}

export const ScansPage: React.FC<ScansPageProps> = ({ onOpenScanModal }) => {
  const scanHistory = [
    {
      id: 'SCAN-2025-0842',
      target: 'http://localhost:8000/chat',
      date: '15 Jul, 2025 10:24 AM',
      duration: '12m 43s',
      status: 'Completed',
      riskScore: 72,
      criticalCount: 6,
      passRate: '68%'
    },
    {
      id: 'SCAN-2025-0841',
      target: 'https://ai-internal.enterprise.com/v1/query',
      date: '14 Jul, 2025 04:15 PM',
      duration: '18m 10s',
      status: 'Completed',
      riskScore: 84,
      criticalCount: 9,
      passRate: '52%'
    },
    {
      id: 'SCAN-2025-0840',
      target: 'http://localhost:8000/chat',
      date: '12 Jul, 2025 09:30 AM',
      duration: '11m 05s',
      status: 'Completed',
      riskScore: 65,
      criticalCount: 4,
      passRate: '74%'
    }
  ];

  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--text-bright)' }}>
            Autonomous Security Assessment Scans
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Historical record of automated red-team simulations and LLM vulnerability evaluations.
          </p>
        </div>

        <button onClick={onOpenScanModal} className="btn-primary-red">
          <Play size={16} fill="white" />
          Launch New Scan
        </button>
      </div>

      <div className="argus-card">
        <div className="argus-card-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Radar size={16} color="var(--accent-red)" />
            <span>Scan History Log</span>
          </div>
        </div>

        <div style={{ padding: '0 20px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>
                <th style={{ padding: '16px 12px' }}>Scan ID</th>
                <th style={{ padding: '16px 12px' }}>Target Endpoint</th>
                <th style={{ padding: '16px 12px' }}>Timestamp</th>
                <th style={{ padding: '16px 12px' }}>Duration</th>
                <th style={{ padding: '16px 12px' }}>Risk Score</th>
                <th style={{ padding: '16px 12px' }}>Critical Vulns</th>
                <th style={{ padding: '16px 12px' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {scanHistory.map((scan) => (
                <tr key={scan.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)', fontSize: '0.85rem' }}>
                  <td style={{ padding: '16px 12px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--accent-blue-glow)' }}>
                    {scan.id}
                  </td>
                  <td style={{ padding: '16px 12px', color: 'var(--text-bright)', fontFamily: 'var(--font-mono)' }}>
                    {scan.target}
                  </td>
                  <td style={{ padding: '16px 12px', color: 'var(--text-secondary)' }}>
                    {scan.date}
                  </td>
                  <td style={{ padding: '16px 12px', color: 'var(--text-muted)' }}>
                    {scan.duration}
                  </td>
                  <td style={{ padding: '16px 12px' }}>
                    <span style={{ fontWeight: 800, color: 'var(--accent-red-glow)' }}>
                      {scan.riskScore}/100
                    </span>
                  </td>
                  <td style={{ padding: '16px 12px' }}>
                    <span className="badge badge-critical">
                      {scan.criticalCount} Critical
                    </span>
                  </td>
                  <td style={{ padding: '16px 12px' }}>
                    <button style={{
                      backgroundColor: 'transparent',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '4px 10px',
                      color: 'var(--text-secondary)',
                      fontSize: '0.78rem',
                      cursor: 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}>
                      Report <ExternalLink size={12} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
