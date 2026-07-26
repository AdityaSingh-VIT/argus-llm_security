import React from 'react';
import { Activity } from 'lucide-react';

interface ScanStatusCardProps {
  onOpenScanModal: () => void;
}

export const ScanStatusCard: React.FC<ScanStatusCardProps> = ({ onOpenScanModal }) => {
  return (
    <div className="argus-card col-span-4" style={{ height: '310px', display: 'flex', flexDirection: 'column' }}>
      <div className="argus-card-header">
        <span>Scan Status</span>
      </div>

      <div style={{
        flex: 1,
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between'
      }}>
        {/* Last Scan Info */}
        <div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Last Scan: <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>15 Jul, 2025 10:24 AM</span>
          </div>

          {/* Stats Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '12px',
            marginTop: '20px',
            textAlign: 'center'
          }}>
            <div style={{
              backgroundColor: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '12px 6px'
            }}>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Scan Duration</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-bright)', marginTop: '4px', fontFamily: 'var(--font-mono)' }}>
                12m 43s
              </div>
            </div>

            <div style={{
              backgroundColor: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '12px 6px'
            }}>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Assets Scanned</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-bright)', marginTop: '4px', fontFamily: 'var(--font-mono)' }}>
                128
              </div>
            </div>

            <div style={{
              backgroundColor: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '12px 6px'
            }}>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Tests Executed</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-bright)', marginTop: '4px', fontFamily: 'var(--font-mono)' }}>
                842
              </div>
            </div>
          </div>
        </div>

        {/* Large Prominent New Scan Button */}
        <button
          onClick={onOpenScanModal}
          className="btn-primary-red"
          style={{
            width: '100%',
            height: '48px',
            fontSize: '1rem',
            letterSpacing: '0.02em',
            position: 'relative'
          }}
        >
          <span>New Scan</span>
          <Activity size={18} className="animate-glow" />
        </button>
      </div>
    </div>
  );
};
