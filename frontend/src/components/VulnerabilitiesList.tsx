import React from 'react';
import { X } from 'lucide-react';

interface VulnItem {
  name: string;
  score: number;
}

export const VulnerabilitiesList: React.FC = () => {
  const vulns: VulnItem[] = [
    { name: 'Prompt Injection', score: 9.8 },
    { name: 'RAG Poisoning', score: 8.7 },
    { name: 'Tool Abuse', score: 7.2 },
    { name: 'Data Leakage', score: 6.5 },
    { name: 'Excessive Agency', score: 4.1 }
  ];

  return (
    <div className="argus-card col-span-4" style={{ height: '310px', display: 'flex', flexDirection: 'column' }}>
      <div className="argus-card-header">
        <span>Top Vulnerabilities</span>
        <X size={15} color="var(--text-muted)" style={{ cursor: 'pointer' }} />
      </div>

      <div style={{
        flex: 1,
        padding: '16px 20px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-around'
      }}>
        {vulns.map((item, idx) => {
          const percent = (item.score / 10) * 100;
          return (
            <div key={idx}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '0.8rem',
                marginBottom: '6px'
              }}>
                <span style={{ color: 'var(--text-bright)', fontWeight: 500 }}>
                  {item.name}
                </span>
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 700,
                  fontSize: '0.78rem',
                  color: item.score > 8 ? 'var(--accent-red-glow)' : 'var(--text-secondary)'
                }}>
                  {item.score.toFixed(1)}<span style={{ color: 'var(--text-muted)' }}>/10</span>
                </span>
              </div>

              {/* Progress Bar Container */}
              <div style={{
                width: '100%',
                height: '6px',
                backgroundColor: 'rgba(255, 255, 255, 0.06)',
                borderRadius: '9999px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${percent}%`,
                  height: '100%',
                  background: item.score > 8 
                    ? 'linear-gradient(90deg, #DC2626 0%, #EF4444 100%)' 
                    : item.score > 6 
                    ? 'linear-gradient(90deg, #D97706 0%, #F59E0B 100%)' 
                    : 'linear-gradient(90deg, #2563EB 0%, #3B82F6 100%)',
                  borderRadius: '9999px',
                  boxShadow: item.score > 8 ? '0 0 8px rgba(239, 68, 68, 0.6)' : 'none',
                  transition: 'width 1s ease-in-out'
                }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
