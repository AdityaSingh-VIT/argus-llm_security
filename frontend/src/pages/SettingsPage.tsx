import React from 'react';
import { Settings, Save } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--text-bright)' }}>
          Platform Settings & API Keys
        </h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          Configure API connections, LLM Red Team keys, and Neo4j credentials.
        </p>
      </div>

      <div className="argus-card" style={{ padding: '24px', maxWidth: '640px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
              FastAPI Backend URL
            </label>
            <input
              type="text"
              defaultValue="http://localhost:8000"
              style={{
                width: '100%', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)', padding: '10px', color: 'white', fontFamily: 'var(--font-mono)', fontSize: '0.85rem'
              }}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
              Neo4j URI
            </label>
            <input
              type="text"
              defaultValue="bolt://localhost:7687"
              style={{
                width: '100%', backgroundColor: 'var(--bg-input)', border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)', padding: '10px', color: 'white', fontFamily: 'var(--font-mono)', fontSize: '0.85rem'
              }}
            />
          </div>

          <button className="btn-primary-red" style={{ marginTop: '10px' }}>
            <Save size={16} /> Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
};
