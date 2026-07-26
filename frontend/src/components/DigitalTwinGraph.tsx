import React, { useState } from 'react';
import { 
  Maximize2, 
  User, 
  Globe, 
  Database, 
  FileText, 
  FolderGit2, 
  Mail, 
  ShieldAlert,
  Cpu
} from 'lucide-react';

interface NodeItem {
  id: string;
  label: string;
  icon: any;
  x: number;
  y: number;
  status: 'normal' | 'risk' | 'critical';
}

export const DigitalTwinGraph: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  // Layout coordinates relative to 500x320 SVG viewport
  const nodes: NodeItem[] = [
    { id: 'llm', label: 'LLM', icon: Cpu, x: 250, y: 170, status: 'critical' },
    { id: 'user', label: 'User', icon: User, x: 80, y: 100, status: 'normal' },
    { id: 'webapp', label: 'Web App', icon: Globe, x: 250, y: 55, status: 'risk' },
    { id: 'vectordb', label: 'Vector DB', icon: Database, x: 420, y: 100, status: 'risk' },
    { id: 'documents', label: 'Documents', icon: FileText, x: 420, y: 240, status: 'normal' },
    { id: 'filesystem', label: 'File System', icon: FolderGit2, x: 300, y: 280, status: 'risk' },
    { id: 'email', label: 'Email API', icon: Mail, x: 100, y: 240, status: 'risk' },
  ];

  // Connection links between center (LLM) and satellite nodes
  const links = [
    { source: 'user', target: 'llm', isRisk: true },
    { source: 'webapp', target: 'llm', isRisk: true },
    { source: 'vectordb', target: 'llm', isRisk: true },
    { source: 'documents', target: 'llm', isRisk: false },
    { source: 'filesystem', target: 'llm', isRisk: true },
    { source: 'email', target: 'llm', isRisk: true },
  ];

  const getNodePos = (id: string) => nodes.find(n => n.id === id) || { x: 0, y: 0 };

  return (
    <div className="argus-card col-span-7" style={{ height: '380px', display: 'flex', flexDirection: 'column' }}>
      <div className="argus-card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ color: 'var(--text-bright)' }}>Attack Surface (Digital Twin)</span>
        </div>
        <Maximize2 size={16} color="var(--text-muted)" style={{ cursor: 'pointer' }} />
      </div>

      <div style={{
        flex: 1,
        position: 'relative',
        backgroundColor: 'rgba(7, 9, 12, 0.4)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden'
      }}>
        {/* SVG Connections & Animations */}
        <svg width="100%" height="100%" viewBox="0 0 500 320" style={{ position: 'absolute', top: 0, left: 0 }}>
          <defs>
            <radialGradient id="llm-glow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="rgba(239, 68, 68, 0.4)" />
              <stop offset="100%" stopColor="rgba(239, 68, 68, 0)" />
            </radialGradient>
          </defs>

          {/* Central Radial Glow */}
          <circle cx="250" cy="170" r="70" fill="url(#llm-glow)" />

          {/* Links */}
          {links.map((link, idx) => {
            const p1 = getNodePos(link.source);
            const p2 = getNodePos(link.target);
            return (
              <g key={idx}>
                <line
                  x1={p1.x}
                  y1={p1.y}
                  x2={p2.x}
                  y2={p2.y}
                  stroke={link.isRisk ? '#EF4444' : '#4B5563'}
                  strokeWidth={link.isRisk ? '2' : '1.5'}
                  strokeDasharray={link.isRisk ? '5,5' : 'none'}
                />
                {link.isRisk && (
                  <circle r="3" fill="#FF2E2E">
                    <animateMotion
                      path={`M ${p1.x} ${p1.y} L ${p2.x} ${p2.y}`}
                      dur="3s"
                      repeatCount="indefinite"
                    />
                  </circle>
                )}
              </g>
            );
          })}
        </svg>

        {/* Render Interactive Nodes */}
        {nodes.map((node) => {
          const Icon = node.icon;
          const isCenter = node.id === 'llm';
          const isSelected = selectedNode === node.id;

          return (
            <div
              key={node.id}
              onClick={() => setSelectedNode(node.id)}
              style={{
                position: 'absolute',
                left: `${(node.x / 500) * 100}%`,
                top: `${(node.y / 320) * 100}%`,
                transform: 'translate(-50%, -50%)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                cursor: 'pointer',
                zIndex: isCenter ? 10 : 5
              }}
            >
              {/* Node Icon Container */}
              <div
                style={{
                  width: isCenter ? '62px' : '46px',
                  height: isCenter ? '62px' : '46px',
                  borderRadius: isCenter ? '16px' : '50%',
                  backgroundColor: isCenter ? '#161B26' : '#11151F',
                  border: isCenter 
                    ? '2px solid #EF4444' 
                    : isSelected 
                    ? '2px solid #3B82F6' 
                    : '1px solid rgba(255, 255, 255, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: isCenter ? '0 0 20px rgba(239, 68, 68, 0.5)' : 'var(--shadow-card)',
                  transition: 'all 0.2s ease'
                }}
              >
                {isCenter ? (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <ShieldAlert size={26} color="#FF2E2E" className="animate-glow" />
                  </div>
                ) : (
                  <Icon size={20} color={isSelected ? '#60A5FA' : '#9CA3AF'} />
                )}
              </div>

              {/* Node Label */}
              <span
                style={{
                  marginTop: '6px',
                  fontSize: isCenter ? '0.85rem' : '0.75rem',
                  fontWeight: isCenter ? 700 : 600,
                  color: isCenter ? '#FFFFFF' : 'var(--text-secondary)',
                  backgroundColor: 'rgba(11, 14, 20, 0.8)',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  border: '1px solid rgba(255, 255, 255, 0.05)',
                  whiteSpace: 'nowrap'
                }}
              >
                {node.label}
              </span>
            </div>
          );
        })}
      </div>

      {/* Graph Legend Footer */}
      <div style={{
        padding: '12px 20px',
        borderTop: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        gap: '24px',
        fontSize: '0.75rem',
        color: 'var(--text-muted)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '16px', height: '2px', backgroundColor: '#6B7280' }} />
          Normal Connection
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '16px', height: '2px', borderTop: '2px dashed #EF4444' }} />
          High Risk Path
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#FF2E2E' }} />
          Data Flow
        </div>
      </div>
    </div>
  );
};
