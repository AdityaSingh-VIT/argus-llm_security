import React from 'react';

export const RiskRadarChart: React.FC = () => {
  // Pentagon radar chart configuration
  const center = 110;
  const radius = 75;
  const categories = [
    { label: 'Prompt Injection', value: 0.95 },
    { label: 'Data Leakage', value: 0.70 },
    { label: 'Excessive Agency', value: 0.45 },
    { label: 'Tool Abuse', value: 0.75 },
    { label: 'RAG Poisoning', value: 0.88 }
  ];

  const numSides = categories.length;
  const angleStep = (2 * Math.PI) / numSides;
  // Offset start angle by -90 deg (-PI/2) to put first vertex at top
  const startAngle = -Math.PI / 2;

  const getCoordinates = (index: number, valFactor: number) => {
    const angle = startAngle + index * angleStep;
    const x = center + radius * valFactor * Math.cos(angle);
    const y = center + radius * valFactor * Math.sin(angle);
    return { x, y };
  };

  // Concentric grid rings (20%, 40%, 60%, 80%, 100%)
  const gridRings = [0.2, 0.4, 0.6, 0.8, 1.0];

  // Radar value polygon points
  const radarPoints = categories.map((cat, idx) => {
    const { x, y } = getCoordinates(idx, cat.value);
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="argus-card col-span-4" style={{ height: '310px', display: 'flex', flexDirection: 'column' }}>
      <div className="argus-card-header">
        <span>Risk Distribution</span>
      </div>

      <div style={{
        flex: 1,
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '10px'
      }}>
        <svg width="220" height="220" viewBox="0 0 220 220" style={{ overflow: 'visible' }}>
          {/* Radial Axis Grid Lines */}
          {categories.map((_, idx) => {
            const { x, y } = getCoordinates(idx, 1.0);
            return (
              <line
                key={idx}
                x1={center}
                y1={center}
                x2={x}
                y2={y}
                stroke="rgba(255, 255, 255, 0.08)"
                strokeWidth="1"
              />
            );
          })}

          {/* Pentagon Concentric Rings */}
          {gridRings.map((ringFactor, rIdx) => {
            const points = categories.map((_, idx) => {
              const { x, y } = getCoordinates(idx, ringFactor);
              return `${x},${y}`;
            }).join(' ');
            return (
              <polygon
                key={rIdx}
                points={points}
                fill="none"
                stroke="rgba(255, 255, 255, 0.07)"
                strokeWidth="1"
              />
            );
          })}

          {/* Value Radar Filled Polygon */}
          <polygon
            points={radarPoints}
            fill="rgba(239, 68, 68, 0.25)"
            stroke="#EF4444"
            strokeWidth="2"
            style={{ filter: 'drop-shadow(0 0 8px rgba(239, 68, 68, 0.6))' }}
          />

          {/* Data Points Dots */}
          {categories.map((cat, idx) => {
            const { x, y } = getCoordinates(idx, cat.value);
            return (
              <circle
                key={idx}
                cx={x}
                cy={y}
                r="3.5"
                fill="#FF2E2E"
                stroke="#FFFFFF"
                strokeWidth="1"
              />
            );
          })}

          {/* Text Labels */}
          {categories.map((cat, idx) => {
            const { x, y } = getCoordinates(idx, 1.25);
            let textAnchor: 'inherit' | 'end' | 'start' | 'middle' | undefined = 'middle';
            if (x < center - 10) textAnchor = 'end';
            if (x > center + 10) textAnchor = 'start';

            return (
              <text
                key={idx}
                x={x}
                y={y}
                fill="var(--text-muted)"
                fontSize="9"
                fontFamily="var(--font-main)"
                fontWeight="500"
                textAnchor={textAnchor}
                dominantBaseline="central"
              >
                {cat.label}
              </text>
            );
          })}
        </svg>
      </div>
    </div>
  );
};
