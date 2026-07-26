import React from 'react';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  changeText: string;
  isIncrease: boolean;
  trendColor: 'red' | 'blue' | 'green';
  sparklineData: number[];
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  changeText,
  isIncrease,
  trendColor,
  sparklineData
}) => {
  const getColorHex = () => {
    switch (trendColor) {
      case 'red': return '#EF4444';
      case 'blue': return '#3B82F6';
      case 'green': return '#10B981';
    }
  };

  const colorHex = getColorHex();

  // Convert sparkline points to SVG path
  const width = 140;
  const height = 36;
  const min = Math.min(...sparklineData);
  const max = Math.max(...sparklineData);
  const range = max - min || 1;

  const points = sparklineData.map((val, idx) => {
    const x = (idx / (sparklineData.length - 1)) * width;
    const y = height - ((val - min) / range) * (height - 8) - 4;
    return `${x},${y}`;
  }).join(' ');

  const ArrowIcon = isIncrease ? ArrowUpRight : ArrowDownRight;

  return (
    <div className="argus-card col-span-3" style={{ height: '220px', padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
          {title}
        </div>
        <div style={{
          fontSize: '2.4rem',
          fontWeight: 800,
          fontFamily: 'var(--font-heading)',
          color: 'var(--text-bright)',
          marginTop: '8px',
          lineHeight: 1
        }}>
          {value}
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          marginTop: '10px',
          fontSize: '0.78rem',
          fontWeight: 600,
          color: isIncrease ? (trendColor === 'red' ? '#EF4444' : '#3B82F6') : '#10B981'
        }}>
          <ArrowIcon size={14} />
          {changeText}
        </div>
      </div>

      {/* Sparkline chart */}
      <div style={{ width: '100%', height: '40px', marginTop: '10px' }}>
        <svg width="100%" height="40" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
          <polyline
            fill="none"
            stroke={colorHex}
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={points}
            style={{ filter: `drop-shadow(0 0 4px ${colorHex})` }}
          />
        </svg>
      </div>
    </div>
  );
};
