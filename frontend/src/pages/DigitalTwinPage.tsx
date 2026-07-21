import React, { useState } from 'react';
import { 
  Network, 
  Search, 
  Database, 
  Cpu, 
  FileText, 
  Mail, 
  User, 
  Globe, 
  Terminal,
  AlertTriangle
} from 'lucide-react';

export const DigitalTwinPage: React.FC = () => {
  const [selectedAsset, setSelectedAsset] = useState<{
    name: string;
    type: string;
    risk: string;
    cypher: string;
    description: string;
  }>({
    name: 'LLM Engine (GPT-4o)',
    type: 'Core AI Model',
    risk: 'CRITICAL (9.8/10)',
    cypher: 'MATCH (u:User)-[r:PROMPT_INJECTION]->(m:LLM)-[:ACCESS]->(t:Tool) RETURN u, m, t',
    description: 'Central orchestration engine with zero prompt sanitization. Subject to direct and indirect prompt injection attacks.'
  });

  return (
    <div className="page-container" style={{ display: 'flex', flexDirection: 'column', gap: '20px', height: 'calc(100vh - 100px)' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--text-bright)' }}>
            Digital Twin & Asset Topology
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Real-time Neo4j knowledge graph of the enterprise AI ecosystem, vector stores, tools, and attack vectors.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <div style={{ position: 'relative' }}>
            <Search size={14} color="var(--text-muted)" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search graph nodes..."
              style={{
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '6px 12px 6px 30px',
                color: 'var(--text-bright)',
                fontSize: '0.82rem',
                outline: 'none'
              }}
            />
          </div>
        </div>
      </div>

      {/* Main Split Layout */}
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 340px', gap: '20px', minHeight: 0 }}>
        {/* Graph Canvas */}
        <div className="argus-card" style={{ display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden' }}>
          <div className="argus-card-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Network size={16} color="var(--accent-red)" />
              <span>Neo4j Graph Visualizer</span>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              128 Nodes | 342 Edges
            </span>
          </div>

          <div style={{
            flex: 1,
            backgroundColor: '#07090C',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative'
          }}>
            {/* Interactive Graph Node Overlay */}
            <div style={{ width: '100%', height: '100%', position: 'relative' }}>
              <svg width="100%" height="100%" viewBox="0 0 700 450">
                {/* Background Grid */}
                <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
                  <path d="M 30 0 L 0 0 0 30" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1"/>
                </pattern>
                <rect width="100%" height="100%" fill="url(#grid)" />

                {/* Edges */}
                <line x1="150" y1="120" x2="350" y2="225" stroke="#EF4444" strokeWidth="2.5" strokeDasharray="6,6" />
                <line x1="350" y1="225" x2="550" y2="120" stroke="#EF4444" strokeWidth="2" strokeDasharray="6,6" />
                <line x1="350" y1="225" x2="550" y2="330" stroke="#4B5563" strokeWidth="1.5" />
                <line x1="350" y1="225" x2="150" y2="330" stroke="#EF4444" strokeWidth="2" strokeDasharray="6,6" />
                <line x1="350" y1="225" x2="350" y2="80" stroke="#3B82F6" strokeWidth="2" />
              </svg>

              {/* Interactive Node Items */}
              <div 
                onClick={() => setSelectedAsset({
                  name: 'LLM Engine (GPT-4o)',
                  type: 'Core AI Model',
                  risk: 'CRITICAL (9.8/10)',
                  cypher: 'MATCH (u:User)-[r:PROMPT_INJECTION]->(m:LLM)-[:ACCESS]->(t:Tool) RETURN u, m, t',
                  description: 'Central orchestration engine with zero prompt sanitization. Subject to direct and indirect prompt injection attacks.'
                })}
                style={{
                  position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
                  padding: '14px 22px', backgroundColor: '#1A1F2C', border: '2px solid #EF4444',
                  borderRadius: 'var(--radius-lg)', boxShadow: '0 0 25px rgba(239,68,68,0.5)', cursor: 'pointer',
                  display: 'flex', alignItems: 'center', gap: '10px'
                }}
              >
                <Cpu size={22} color="#FF2E2E" />
                <div>
                  <div style={{ fontWeight: 800, color: 'white', fontSize: '0.9rem' }}>LLM Core Engine</div>
                  <div style={{ fontSize: '0.7rem', color: '#F87171' }}>Target Node</div>
                </div>
              </div>

              <div 
                onClick={() => setSelectedAsset({
                  name: 'Email Exfiltration API',
                  type: 'External Tool Integration',
                  risk: 'HIGH (8.5/10)',
                  cypher: 'MATCH (m:LLM)-[r:CALLS]->(t:EmailAPI) WHERE r.sanitized = false RETURN t',
                  description: 'SMTP Email relay service callable directly by the LLM without secondary user approval.'
                })}
                style={{
                  position: 'absolute', bottom: '20%', left: '20%', transform: 'translate(-50%, 0)',
                  padding: '10px 16px', backgroundColor: '#11151F', border: '1px solid #EF4444',
                  borderRadius: 'var(--radius-md)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px'
                }}
              >
                <Mail size={18} color="#F59E0B" />
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'white' }}>Email API Tool</span>
              </div>

              <div 
                onClick={() => setSelectedAsset({
                  name: 'Vector Database (ChromaDB)',
                  type: 'RAG Knowledge Store',
                  risk: 'HIGH (8.7/10)',
                  cypher: 'MATCH (p:PDF)-[:EMBEDDED_IN]->(v:VectorDB)-[:RETRIEVED_BY]->(m:LLM) RETURN p, v, m',
                  description: 'Contains company handbook and employee compensation vector embeddings susceptible to RAG poisoning.'
                })}
                style={{
                  position: 'absolute', top: '22%', right: '18%', transform: 'translate(0, -50%)',
                  padding: '10px 16px', backgroundColor: '#11151F', border: '1px solid #EF4444',
                  borderRadius: 'var(--radius-md)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px'
                }}
              >
                <Database size={18} color="#60A5FA" />
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'white' }}>Vector DB (Chroma)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Node Inspector Panel */}
        <div className="argus-card" style={{ display: 'flex', flexDirection: 'column', padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '12px' }}>
            <AlertTriangle size={18} color="var(--accent-red)" />
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-bright)' }}>Node Inspector</h3>
          </div>

          <div style={{ flex: 1, marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '16px', overflowY: 'auto' }}>
            <div>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Asset Name</span>
              <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-bright)', marginTop: '2px' }}>{selectedAsset.name}</div>
            </div>

            <div>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Asset Category</span>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>{selectedAsset.type}</div>
            </div>

            <div>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Threat Rating</span>
              <div style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--accent-red-glow)', marginTop: '2px' }}>{selectedAsset.risk}</div>
            </div>

            <div>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Description</span>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: 1.4 }}>
                {selectedAsset.description}
              </p>
            </div>

            <div>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Terminal size={12} /> Cypher Graph Query
              </span>
              <div style={{
                backgroundColor: 'rgba(0,0,0,0.5)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '10px',
                marginTop: '6px',
                fontSize: '0.72rem',
                color: 'var(--accent-blue-glow)',
                fontFamily: 'var(--font-mono)',
                wordBreak: 'break-all',
                lineHeight: 1.4
              }}>
                {selectedAsset.cypher}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
