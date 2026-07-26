import React from 'react';
import { 
  ShieldAlert, 
  Radar, 
  Network, 
  Bug, 
  GitPullRequest, 
  BrainCircuit, 
  FileText, 
  Blocks, 
  Settings,
  ChevronDown,
  Activity
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'scans', label: 'Scans', icon: Radar },
    { id: 'digital-twin', label: 'Digital Twin', icon: Network },
    { id: 'vulnerabilities', label: 'Vulnerabilities', icon: Bug },
    { id: 'attack-paths', label: 'Attack Paths', icon: GitPullRequest },
    { id: 'threat-intel', label: 'Threat Intelligence', icon: BrainCircuit },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'integrations', label: 'Integrations', icon: Blocks },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside style={{
      width: '260px',
      height: '100vh',
      backgroundColor: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border-subtle)',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
      userSelect: 'none'
    }}>
      {/* Brand Header */}
      <div style={{
        padding: '24px 20px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.05)'
      }}>
        <img 
          src="/logo.png" 
          alt="ARGUS Logo" 
          style={{
            width: '38px',
            height: '38px',
            objectFit: 'contain',
            filter: 'drop-shadow(0 0 8px rgba(239, 68, 68, 0.5))'
          }}
        />
        <div>
          <h1 style={{
            fontFamily: 'var(--font-heading)',
            fontSize: '1.45rem',
            fontWeight: 800,
            letterSpacing: '0.08em',
            color: '#FFFFFF',
            lineHeight: 1
          }}>
            ARGUS
          </h1>
          <span style={{
            fontSize: '0.62rem',
            color: 'var(--accent-red)',
            letterSpacing: '0.12em',
            fontWeight: 700,
            textTransform: 'uppercase'
          }}>
            AI SECURITY PLATFORM
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{
        flex: 1,
        padding: '16px 12px',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
        overflowY: 'auto'
      }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
                padding: '10px 14px',
                borderRadius: 'var(--radius-md)',
                border: 'none',
                backgroundColor: isActive ? 'var(--accent-red-bg)' : 'transparent',
                color: isActive ? 'var(--accent-red-glow)' : 'var(--text-secondary)',
                fontWeight: isActive ? 600 : 400,
                fontSize: '0.9rem',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                borderLeft: isActive ? '3px solid var(--accent-red)' : '3px solid transparent'
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.03)';
                  e.currentTarget.style.color = 'var(--text-primary)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }
              }}
            >
              <Icon size={18} color={isActive ? 'var(--accent-red)' : 'currentColor'} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* User Footer Profile */}
      <div style={{
        padding: '16px 16px',
        borderTop: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: 'rgba(0,0,0,0.2)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            position: 'relative',
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            backgroundColor: '#1E2433',
            border: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 700,
            color: 'var(--text-bright)',
            fontSize: '0.85rem'
          }}>
            ST
            <span style={{
              position: 'absolute',
              bottom: 0,
              right: 0,
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: 'var(--accent-green)',
              border: '2px solid var(--bg-sidebar)'
            }} />
          </div>
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-bright)' }}>
              SOC Team
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Administrator
            </div>
          </div>
        </div>
        <ChevronDown size={16} color="var(--text-muted)" style={{ cursor: 'pointer' }} />
      </div>
    </aside>
  );
};
