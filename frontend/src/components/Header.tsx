import React from 'react';
import { Search, Bell, Moon, Plus } from 'lucide-react';

interface HeaderProps {
  onOpenScanModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenScanModal }) => {
  return (
    <header style={{
      height: '64px',
      borderBottom: '1px solid var(--border-subtle)',
      backgroundColor: 'rgba(9, 12, 16, 0.7)',
      backdropFilter: 'blur(12px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 32px',
      position: 'sticky',
      top: 0,
      zIndex: 40
    }}>
      {/* Search Input */}
      <div style={{
        position: 'relative',
        width: '380px'
      }}>
        <Search size={16} color="var(--text-muted)" style={{
          position: 'absolute',
          left: '14px',
          top: '50%',
          transform: 'translateY(-50%)'
        }} />
        <input 
          type="text" 
          placeholder="Search threats, assets, scans..."
          style={{
            width: '100%',
            backgroundColor: 'var(--bg-input)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '8px 40px 8px 38px',
            color: 'var(--text-primary)',
            fontSize: '0.85rem',
            outline: 'none',
            transition: 'all 0.15s ease'
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = 'var(--accent-red)';
            e.currentTarget.style.boxShadow = '0 0 10px rgba(239, 68, 68, 0.2)';
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-subtle)';
            e.currentTarget.style.boxShadow = 'none';
          }}
        />
        <div style={{
          position: 'absolute',
          right: '10px',
          top: '50%',
          transform: 'translateY(-50%)',
          backgroundColor: 'rgba(255, 255, 255, 0.06)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '4px',
          padding: '2px 6px',
          fontSize: '0.7rem',
          color: 'var(--text-muted)',
          fontFamily: 'var(--font-mono)'
        }}>
          ⌘K
        </div>
      </div>

      {/* Action Controls & Admin Profile */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <button 
          onClick={onOpenScanModal}
          style={{
            background: 'var(--accent-red-bg)',
            border: '1px solid var(--accent-red)',
            color: 'var(--accent-red-glow)',
            borderRadius: 'var(--radius-md)',
            padding: '7px 14px',
            fontSize: '0.82rem',
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'all 0.2s ease'
          }}
        >
          <Plus size={14} />
          New Assessment
        </button>

        {/* Notifications */}
        <div style={{
          position: 'relative',
          width: '38px',
          height: '38px',
          borderRadius: '50%',
          backgroundColor: 'var(--bg-input)',
          border: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer'
        }}>
          <Bell size={17} color="var(--text-secondary)" />
          <span style={{
            position: 'absolute',
            top: '2px',
            right: '2px',
            width: '15px',
            height: '15px',
            borderRadius: '50%',
            backgroundColor: 'var(--accent-red)',
            color: 'white',
            fontSize: '0.62rem',
            fontWeight: 800,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            1
          </span>
        </div>

        {/* Dark Mode Toggle */}
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '50%',
          backgroundColor: 'var(--bg-input)',
          border: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer'
        }}>
          <Moon size={17} color="var(--text-secondary)" />
        </div>

        {/* User Profile Avatar */}
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #1F2937 0%, #374151 100%)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 700,
          color: 'var(--text-bright)',
          fontSize: '0.9rem',
          cursor: 'pointer'
        }}>
          A
        </div>
      </div>
    </header>
  );
};
