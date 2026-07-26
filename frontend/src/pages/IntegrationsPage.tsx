import React from 'react';
import { Blocks, CheckCircle2 } from 'lucide-react';

export const IntegrationsPage: React.FC = () => {
  const integrations = [
    { name: 'Neo4j Graph Database', status: 'Connected', desc: 'Stores Digital Twin topology and path Cypher queries.' },
    { name: 'ChromaDB / FAISS', status: 'Connected', desc: 'Monitors vector embeddings for RAG poisoning.' },
    { name: 'Slack Security Alerts', status: 'Active', desc: 'Sends instant webhooks when Critical prompt injection occurs.' },
    { name: 'Jira Software', status: 'Configured', desc: 'Automatically files vulnerability tickets for engineering teams.' }
  ];

  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--text-bright)' }}>
          Enterprise Integrations
        </h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          Connect ARGUS with your SIEM, SOC webhooks, vector databases, and developer ticketing systems.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {integrations.map((item, idx) => (
          <div key={idx} className="argus-card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ fontWeight: 700, color: 'var(--text-bright)', fontSize: '0.95rem' }}>{item.name}</div>
              <span className="badge badge-low"><CheckCircle2 size={12} /> {item.status}</span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '10px' }}>
              {item.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
