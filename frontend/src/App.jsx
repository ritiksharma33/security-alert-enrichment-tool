import React, { useState } from 'react';
import Terminal from './components/Terminal';
import { 
  ShieldAlert, ShieldCheck, ShieldQuestion, Search, Activity, Zap, 
  Globe, FileSearch, Database, Settings, ChevronRight, Shield, Download, Trash2
} from 'lucide-react';
import './App.css';

function App() {
  // --- STATE MANAGEMENT ---
  const [currentModule, setCurrentModule] = useState('ip-enrichment');
  const [isProcessing, setIsProcessing] = useState(false);

  // IP Module
  const [ip, setIp] = useState('');
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);

  // Domain Module
  const [domain, setDomain] = useState('');
  const [domainResult, setDomainResult] = useState(null);
  const [isDomainLoading, setIsDomainLoading] = useState(false);

  // Bulk Module
  const [bulkResults, setBulkResults] = useState([]);
  const [isBulkLoading, setIsBulkLoading] = useState(false);

  const modules = [
    { id: 'ip-enrichment', name: 'IP Intel', icon: <Shield size={20} /> },
    { id: 'domain-intel', name: 'Domain Lookup', icon: <Globe size={20} /> },
    { id: 'file-hash', name: 'Hash Analysis', icon: <FileSearch size={20} /> },
    { id: 'bulk-scan', name: 'CSV Bulk Scan', icon: <Database size={20} /> },
  ];

  // --- LOGIC: IP ENRICHMENT ---
  const startEnrichment = () => {
    if (!ip) return;
    setLogs([]);
    setResult(null);
    setIsProcessing(true);
    const eventSource = new EventSource(`http://127.0.0.1:8000/api/enrich/stream?ip=${ip}`);
    eventSource.onmessage = (event) => {
      const message = event.data;
      setLogs((prev) => [...prev, message]);
      if (message.includes("[COMPLETE]")) {
        eventSource.close();
        fetchFinalResult();
      }
    };
    eventSource.onerror = () => {
      setLogs((prev) => [...prev, "[ERROR] Connection failed."]);
      eventSource.close();
      setIsProcessing(false);
    };
  };

  const fetchFinalResult = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/enrich', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source_ip: ip, event: "Manual UI Scan" })
      });
      const data = await response.json();
      setResult(data);
      setIsProcessing(false);
    } catch (error) { console.error(error); }
  };

  // --- LOGIC: DOMAIN LOOKUP ---
  const startDomainLookup = async () => {
    if (!domain) return;
    setIsDomainLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/domain?domain=${domain}`);
      const data = await response.json();
      setDomainResult(data);
    } catch (error) { console.error(error); }
    finally { setIsDomainLoading(false); }
  };

  // --- UI HELPERS ---
  const getRiskIcon = (level) => {
    switch (level) {
      case 'CRITICAL': return <ShieldAlert color="#ff4d4d" size={64} className="glow-icon" />;
      case 'WARNING': return <ShieldAlert color="#f1c40f" size={64} />;
      case 'SUSPICIOUS': return <ShieldQuestion color="#ffa500" size={64} />;
      case 'SAFE': return <ShieldCheck color="#00ff88" size={64} />;
      default: return <Activity size={64} />;
    }
  };

  return (
    <div className="app-layout">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="sidebar-brand"><Zap size={24} className="brand-icon" /><span>SOAR HUB</span></div>
        <nav className="sidebar-nav">
          {modules.map((mod) => (
            <button key={mod.id} className={`nav-item ${currentModule === mod.id ? 'active' : ''}`} onClick={() => setCurrentModule(mod.id)}>
              {mod.icon}<span className="nav-label">{mod.name}</span>
              {currentModule === mod.id && <ChevronRight size={14} className="active-arrow" />}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer"><button className="nav-item"><Settings size={20} /> <span>Settings</span></button></div>
      </aside>

      {/* MAIN VIEWPORT */}
      <main className="main-viewport">
        <header className="module-header">
          <div className="header-left">
            <h1>{modules.find(m => m.id === currentModule)?.name}</h1>
            <p>Intelligence Platform v2.0</p>
          </div>
          <div className="system-status"><Activity size={16} /> <span>System Online</span></div>
        </header>

        <div className="module-content">
          {/* 1. IP MODULE */}
          {currentModule === 'ip-enrichment' && (
            <div className="module-fade-in">
              <div className="search-box">
                <Search size={20} />
                <input type="text" placeholder="Enter IP..." value={ip} onChange={(e) => setIp(e.target.value)} />
                <button onClick={startEnrichment} disabled={isProcessing}>{isProcessing ? 'Analyzing...' : 'Analyze'}</button>
              </div>
              <section className="display-grid">
                <Terminal logs={logs} />
                <div className="result-panel">
                  {result ? (
                    <div className={`result-card ${result.risk_level.toLowerCase()}`}>
                      <h3>RISK: {result.risk_level}</h3>
                      <div className="stats-container">
                        <div className="stat-item"><span>IP</span><strong>{result.source_ip}</strong></div>
                        <div className="stat-item"><span>SCORE</span><strong>{result.threat_intel.abuse_confidence_score}%</strong></div>
                        <div className="stat-item"><span>REPORTS</span><strong>{result.threat_intel.total_reports}</strong></div>
                        <div className="stat-item"><span>ORIGIN</span><strong>{result.threat_intel.country_code}</strong></div>
                      </div>
                      <div className="icon-wrapper">{getRiskIcon(result.risk_level)}</div>
                    </div>
                  ) : <div className="empty-state"><Shield size={48} opacity={0.1} /><p>Awaiting Input</p></div>}
                </div>
              </section>
            </div>
          )}

          {/* 2. DOMAIN MODULE */}
          {currentModule === 'domain-intel' && (
            <div className="module-fade-in">
              <div className="search-box">
                <Globe size={20} />
                <input type="text" placeholder="Enter Domain..." value={domain} onChange={(e) => setDomain(e.target.value)} />
                <button onClick={startDomainLookup} disabled={isDomainLoading}>{isDomainLoading ? 'WHOIS...' : 'Check'}</button>
              </div>
              {domainResult && (
                <div className={`result-card ${domainResult.risk_level.toLowerCase()} domain-full-width`}>
                  <h3>{domainResult.risk_level}</h3>
                  <div className="stats-container">
                    <div className="stat-item"><span>REGISTRAR</span><strong>{domainResult.registrar}</strong></div>
                    <div className="stat-item"><span>AGE</span><strong>{domainResult.age_days} Days</strong></div>
                    <div className="stat-item"><span>STATUS</span><strong>{domainResult.status}</strong></div>
                  </div>
                  <div className="icon-wrapper">{getRiskIcon(domainResult.risk_level)}</div>
                </div>
              )}
            </div>
          )}

          {/* 3. BULK SCAN MODULE */}
          {currentModule === 'bulk-scan' && (
            <div className="module-fade-in">
              <div className="upload-area">
                <Database size={48} opacity={0.2} />
                <h3>CSV Batch Analysis</h3>
                <input type="file" accept=".csv" id="csv-up" style={{display:'none'}} onChange={async (e) => {
                  const file = e.target.files[0];
                  setIsBulkLoading(true);
                  const fd = new FormData(); fd.append('file', file);
                  const res = await fetch('http://127.0.0.1:8000/api/bulk-scan', { method: 'POST', body: fd });
                  const data = await res.json();
                  setBulkResults(data.data);
                  setIsBulkLoading(false);
                }}/>
                <label htmlFor="csv-up" className="upload-button">{isBulkLoading ? 'Processing...' : 'Upload CSV'}</label>
              </div>

              {bulkResults.length > 0 && (
                <div className="bulk-table-container">
                  <div className="table-actions">
                    <button onClick={() => setBulkResults([])} className="clear-btn"><Trash2 size={16}/> Clear</button>
                  </div>
                  <table className="bulk-table">
                    <thead><tr><th>IP</th><th>Risk</th><th>Score</th><th>Country</th></tr></thead>
                    <tbody>
                      {bulkResults.map((r, i) => (
                        <tr key={i} className={`row-${r.risk.toLowerCase()}`}>
                          <td>{r.ip}</td>
                          <td>{r.risk}</td>
                          <td>{r.score}%</td>
                          <td>{r.country}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* 4. PLACEHOLDERS */}
          {currentModule === 'file-hash' && (
            <div className="placeholder-view">
              <FileSearch size={64} opacity={0.1} />
              <h2>Hash Analysis Module</h2>
              <p>Integration in progress (VirusTotal API).</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;