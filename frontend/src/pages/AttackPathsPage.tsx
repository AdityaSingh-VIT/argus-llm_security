import React from 'react';
import { GitPullRequest, ShieldAlert, ArrowRight } from 'lucide-react';

export const AttackPathsPage: React.FC = () => {
  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--text-bright)' }}>
          Exploit Attack Path Analysis
        </h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          Calculated graph paths mapping how external adversaries can traverse from untrusted prompts to confidential databases.
        </p>
      </div>

      <div className="argus-card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <ShieldAlert size={20} color="var(--accent-red)" />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-bright)' }}>
            Path #1: Indirect Prompt Injection → RAG Poisoning → Email Exfiltration
          </h3>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          backgroundColor: 'rgba(0,0,0,0.4)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
          padding: '20px',
          overflowX: 'auto'
        }}>
          {['Attacker PDF Upload', 'ChromaDB Vector Store', 'RAG Chunk Retrieval', 'LLM Prompt Context', 'Email API Tool', 'Attacker Email'].map((step, idx, arr) => (
            <React.Fragment key={idx}>
              <div style={{
                padding: '10px 16px',
                backgroundColor: idx === 0 || idx === arr.length - 1 ? 'var(--accent-red-bg)' : 'var(--bg-card)',
                border: idx === 0 || idx === arr.length - 1 ? '1px solid var(--accent-red)' : '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-bright)',
                fontSize: '0.82rem',
                fontWeight: 700,
                whiteSpace: 'nowrap'
              }}>
                {step}
              </div>
              {idx < arr.length - 1 && <ArrowRight size={18} color="var(--accent-red)" />}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};
