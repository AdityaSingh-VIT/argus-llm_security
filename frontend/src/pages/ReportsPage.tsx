import React from 'react';
import { FileText, Download, Share2 } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--text-bright)' }}>
          Security Assessment Reports & Audits
        </h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          Generate CISO executive summaries, OWASP compliance reports, and developer remediation guides.
        </p>
      </div>

      <div className="argus-card" style={{ padding: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-bright)' }}>
            Executive OWASP LLM Audit Summary — Q3 2025
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Comprehensive assessment of AI Chatbot RAG architecture, tool permissions, and prompt injection vulnerabilities.
          </p>
        </div>
        <button className="btn-primary-red" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
          <Download size={14} /> Download PDF
        </button>
      </div>
    </div>
  );
};
