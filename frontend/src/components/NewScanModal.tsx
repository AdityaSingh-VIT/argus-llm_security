import React, { useState } from 'react';
import { X, Play, ShieldAlert, CheckCircle2, Loader2 } from 'lucide-react';

interface NewScanModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NewScanModal: React.FC<NewScanModalProps> = ({ isOpen, onClose }) => {
  const [targetUrl, setTargetUrl] = useState('http://localhost:8000/chat');
  const [targetModel, setTargetModel] = useState('GPT-4o (Chatbot API)');
  const [selectedAttacks, setSelectedAttacks] = useState<string[]>([
    'prompt-injection', 'rag-poisoning', 'tool-abuse', 'jailbreak'
  ]);
  const [isScanning, setIsScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [scanComplete, setScanComplete] = useState(false);

  if (!isOpen) return null;

  const toggleAttack = (id: string) => {
    if (selectedAttacks.includes(id)) {
      setSelectedAttacks(selectedAttacks.filter(a => a !== id));
    } else {
      setSelectedAttacks([...selectedAttacks, id]);
    }
  };

  const handleStartScan = () => {
    setIsScanning(true);
    setProgress(15);
    
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsScanning(false);
          setScanComplete(true);
          return 100;
        }
        return prev + 25;
      });
    }, 600);
  };

  const handleReset = () => {
    setIsScanning(false);
    setProgress(0);
    setScanComplete(false);
    onClose();
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100
    }}>
      <div style={{
        width: '540px',
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-glow)',
        borderRadius: 'var(--radius-xl)',
        boxShadow: 'var(--shadow-glow-red)',
        overflow: 'hidden'
      }}>
        {/* Modal Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'rgba(239, 68, 68, 0.05)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ShieldAlert size={20} color="var(--accent-red-glow)" />
            <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-bright)' }}>
              Launch Autonomous AI Red Team Scan
            </h2>
          </div>
          <X size={18} color="var(--text-muted)" style={{ cursor: 'pointer' }} onClick={onClose} />
        </div>

        {/* Modal Body */}
        <div style={{ padding: '24px' }}>
          {!isScanning && !scanComplete && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              <div>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
                  Target LLM Endpoint / Chatbot URL
                </label>
                <input
                  type="text"
                  value={targetUrl}
                  onChange={(e) => setTargetUrl(e.target.value)}
                  style={{
                    width: '100%',
                    backgroundColor: 'var(--bg-input)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '10px 14px',
                    color: 'var(--text-bright)',
                    fontSize: '0.9rem',
                    outline: 'none',
                    fontFamily: 'var(--font-mono)'
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>
                  Target AI Architecture
                </label>
                <select
                  value={targetModel}
                  onChange={(e) => setTargetModel(e.target.value)}
                  style={{
                    width: '100%',
                    backgroundColor: 'var(--bg-input)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '10px 14px',
                    color: 'var(--text-bright)',
                    fontSize: '0.9rem',
                    outline: 'none'
                  }}
                >
                  <option>GPT-4o (Chatbot API + RAG)</option>
                  <option>Claude 3.5 Sonnet (LangChain Tool Agent)</option>
                  <option>Gemini 1.5 Pro (Enterprise RAG)</option>
                  <option>Custom Local Llama3 Endpoint</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '10px' }}>
                  OWASP LLM Attack Suites
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  {[
                    { id: 'prompt-injection', label: 'Prompt Injection (Direct & Indirect)' },
                    { id: 'rag-poisoning', label: 'RAG Knowledge Base Poisoning' },
                    { id: 'tool-abuse', label: 'Unsafe Tool & API Abuse' },
                    { id: 'jailbreak', label: 'Jailbreak & Guardrail Bypass' }
                  ].map((suite) => {
                    const active = selectedAttacks.includes(suite.id);
                    return (
                      <div
                        key={suite.id}
                        onClick={() => toggleAttack(suite.id)}
                        style={{
                          padding: '10px 12px',
                          borderRadius: 'var(--radius-md)',
                          border: active ? '1px solid var(--accent-red)' : '1px solid var(--border-subtle)',
                          backgroundColor: active ? 'var(--accent-red-bg)' : 'var(--bg-input)',
                          color: active ? 'var(--text-bright)' : 'var(--text-muted)',
                          fontSize: '0.78rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          transition: 'all 0.15s ease'
                        }}
                      >
                        <input type="checkbox" checked={active} readOnly style={{ accentColor: 'var(--accent-red)' }} />
                        {suite.label}
                      </div>
                    );
                  })}
                </div>
              </div>

              <button
                onClick={handleStartScan}
                className="btn-primary-red"
                style={{ width: '100%', marginTop: '10px' }}
              >
                <Play size={16} fill="white" />
                Execute Red Team Assessment
              </button>
            </div>
          )}

          {isScanning && (
            <div style={{ padding: '30px 10px', textAlign: 'center' }}>
              <Loader2 size={44} color="var(--accent-red)" className="animate-spin" style={{ margin: '0 auto 20px' }} />
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-bright)' }}>
                ARGUS Autonomous Red Team Engine Running...
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                Executing automated OWASP Top 10 attack payloads against {targetUrl}
              </p>

              {/* Progress bar */}
              <div style={{
                width: '100%',
                height: '8px',
                backgroundColor: 'rgba(255, 255, 255, 0.08)',
                borderRadius: '9999px',
                marginTop: '24px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${progress}%`,
                  height: '100%',
                  backgroundColor: 'var(--accent-red)',
                  boxShadow: '0 0 10px var(--accent-red)',
                  transition: 'width 0.4s ease'
                }} />
              </div>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '8px', display: 'block', fontFamily: 'var(--font-mono)' }}>
                {progress}% Completed
              </span>
            </div>
          )}

          {scanComplete && (
            <div style={{ padding: '20px 10px', textAlign: 'center' }}>
              <CheckCircle2 size={48} color="var(--accent-green)" style={{ margin: '0 auto 16px' }} />
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-bright)' }}>
                Assessment Completed Successfully!
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                Discovered 2 new high-risk attack paths. Digital Twin updated in Neo4j graph.
              </p>
              <button
                onClick={handleReset}
                className="btn-primary-red"
                style={{ width: '100%', marginTop: '24px' }}
              >
                View Assessment Results
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
