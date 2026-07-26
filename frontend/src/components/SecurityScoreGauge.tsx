import React from 'react';
import { X, Flame } from 'lucide-react';

interface SecurityScoreGaugeProps {
  score: number;
}

export const SecurityScoreGauge: React.FC<SecurityScoreGaugeProps> = ({ score }) => {
  // Semi-circle gauge calculation
  const radius = 62;
  const circumference = Math.PI * radius; // 180 deg semi circle
  const scorePercent = Math.min(Math.max(score, 0), 100);
  const strokeDashoffset = circumference - (scorePercent / 100) * circumference;

  return (
    <div className="argus-card col-span-3" style={{ height: '220px', display: 'flex', flexDirection: 'column' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '16px 20px 0',
        color: 'var(--text-secondary)',
        fontSize: '0.88rem',
        fontWeight: 600
      }}>
        <span>Security Score</span>
        <X size={15} color="var(--text-muted)" style={{ cursor: 'pointer' }} />
      </div>

      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        paddingTop: '10px'
      }}>
        {/* SVG Semi Circle Gauge */}
        <div style={{ position: 'relative', width: '150px', height: '85px' }}>
          <svg width="150" height="90" viewBox="0 0 150 90">
            {/* Background Arc */}
            <path
              d="M 15 80 A 60 60 0 0 1 135 80"
              fill="none"
              stroke="rgba(255, 255, 255, 0.08)"
              strokeWidth="12"
              strokeLinecap="round"
            />
            {/* Filled Arc */}
            <path
              d="M 15 80 A 60 60 0 0 1 135 80"
              fill="none"
              stroke="url(#score-gradient)"
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
            />
            <defs>
              <linearGradient id="score-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#F59E0B" />
                <stop offset="100%" stopColor="#EF4444" />
              </linearGradient>
            </defs>
          </svg>

          {/* Number Display */}
          <div style={{
            position: 'absolute',
            bottom: '0',
            left: '50%',
            transform: 'translateX(-50%)',
            textAlign: 'center'
          }}>
            <span style={{
              fontSize: '2.1rem',
              fontWeight: 800,
              fontFamily: 'var(--font-heading)',
              color: 'var(--text-bright)',
              lineHeight: 1
            }}>
              {score}
            </span>
            <span style={{
              fontSize: '0.72rem',
              color: 'var(--text-muted)',
              display: 'block',
              marginTop: '2px'
            }}>
              / 100
            </span>
          </div>
        </div>

        {/* Status Pill */}
        <div style={{
          marginTop: '14px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '3px 12px',
          borderRadius: '9999px',
          backgroundColor: 'var(--accent-red-bg)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          color: 'var(--accent-red-glow)',
          fontSize: '0.75rem',
          fontWeight: 700
        }}>
          <Flame size={12} fill="var(--accent-red)" color="var(--accent-red)" />
          High Risk
        </div>
      </div>
    </div>
  );
};
