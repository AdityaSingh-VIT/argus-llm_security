import React from 'react';
import { BrainCircuit, Globe, Flame } from 'lucide-react';

export const ThreatIntelPage: React.FC = () => {
  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--text-bright)' }}>
          LLM Threat Intelligence Feed
        </h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          Real-time global zero-day jailbreaks, CVEs, and prompt injection techniques feed.
        </p>
      </div>

      <div className="argus-card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <BrainCircuit size={20} color="var(--accent-blue-glow)" />
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-bright)' }}>
            Latest Zero-Day Jailbreak: "Crescendo Multi-Turn Payload"
          </h3>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '10px', lineHeight: 1.5 }}>
          Gradual multi-turn dialogue technique that bypasses standard single-turn LLM input classifiers by slowly steering model context towards forbidden actions.
        </p>
      </div>
    </div>
  );
};
