import React from 'react';

interface AttackEvent {
  time: string;
  type: string;
  description: string;
  severity: 'Critical' | 'High' | 'Low';
}

export const AttackTimeline: React.FC = () => {
  const events: AttackEvent[] = [
    {
      time: '10:24 AM',
      type: 'Prompt Injection',
      description: 'System prompt leaked via PDF',
      severity: 'Critical'
    },
    {
      time: '10:21 AM',
      type: 'Jailbreak Attempt',
      description: 'Model tried to bypass guardrails',
      severity: 'High'
    },
    {
      time: '10:17 AM',
      type: 'RAG Poisoning',
      description: 'Malicious doc detected',
      severity: 'Critical'
    },
    {
      time: '10:12 AM',
      type: 'Tool Abuse',
      description: 'Email exfiltration attempt',
      severity: 'High'
    },
    {
      time: '10:08 AM',
      type: 'Indirect Prompt Injection',
      description: 'Sensitive data exposure',
      severity: 'Low'
    }
  ];

  const getBadgeClass = (severity: string) => {
    switch (severity) {
      case 'Critical': return 'badge-critical';
      case 'High': return 'badge-high';
      default: return 'badge-low';
    }
  };

  const getDotColor = (severity: string) => {
    switch (severity) {
      case 'Critical': return '#EF4444';
      case 'High': return '#F59E0B';
      default: return '#10B981';
    }
  };

  return (
    <div className="argus-card col-span-5" style={{ height: '380px', display: 'flex', flexDirection: 'column' }}>
      <div className="argus-card-header">
        <span>Recent Attack Timeline</span>
        <a href="#view-all" style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textDecoration: 'none' }}>
          View All
        </a>
      </div>

      <div style={{
        flex: 1,
        padding: '16px 20px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        {events.map((event, idx) => (
          <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '14px', position: 'relative' }}>
            {/* Timeline Vertical Bar */}
            {idx < events.length - 1 && (
              <div style={{
                position: 'absolute',
                left: '60px',
                top: '18px',
                bottom: '-16px',
                width: '1px',
                backgroundColor: 'rgba(255, 255, 255, 0.08)'
              }} />
            )}

            {/* Timestamp */}
            <div style={{
              width: '54px',
              fontSize: '0.72rem',
              color: 'var(--text-muted)',
              fontFamily: 'var(--font-mono)',
              paddingTop: '2px',
              textAlign: 'right'
            }}>
              {event.time}
            </div>

            {/* Event Dot */}
            <div style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: getDotColor(event.severity),
              marginTop: '4px',
              boxShadow: `0 0 8px ${getDotColor(event.severity)}`
            }} />

            {/* Event Info */}
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-bright)' }}>
                  {event.type}
                </span>
                <span className={`badge ${getBadgeClass(event.severity)}`}>
                  {event.severity}
                </span>
              </div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                {event.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
