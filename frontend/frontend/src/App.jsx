import React, { useState } from 'react';
import Terminal from './components/Terminal';
import { ShieldAlert, ShieldCheck, ShieldQuestion, Search, Activity, Zap } from 'lucide-react';
import './App.css';

function App() {
  const [ip, setIp] = useState('');
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

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
      setLogs((prev) => [...prev, "[ERROR] Connection to backend lost."]);
      eventSource.close();
      setIsProcessing(false);
    };
  };

  const fetchFinalResult = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/enrich', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            alert_id: "UI-" + Math.floor(Math.random() * 1000),
            source_ip: ip,
            event: "Manual UI Scan"
        })
      });
      const data = await response.json();
      setResult(data);
      setIsProcessing(false);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  // Helper to render the correct icon based on Risk Level
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
    <div className="dashboard-container">
      <header>
        <h1><Zap size={32} className="accent-icon" /> SOAR <span className="highlight">Enrichment Hub</span></h1>
        <p>Real-Time Threat Intelligence & Heuristic Analysis</p>
      </header>

      <main className="main-content">
        <section className="input-section">
          <div className="search-box">
            <Search className="search-icon" />
            <input 
              type="text" 
              placeholder="Target IP Address..." 
              value={ip}
              onChange={(e) => setIp(e.target.value)}
              disabled={isProcessing}
            />
            <button onClick={startEnrichment} disabled={isProcessing}>
              {isProcessing ? 'Analyzing...' : 'Execute Playbook'}
            </button>
          </div>
        </section>

        <section className="display-grid">
          <Terminal logs={logs} />
          
          <div className="result-panel">
            {!result && !isProcessing && (
              <div className="empty-state">
                <ShieldQuestion size={48} opacity={0.2} />
                <p>Awaiting Intelligence Input...</p>
              </div>
            )}
            
            {isProcessing && <div className="loader-ring"><div></div><div></div></div>}

            {result && (
              <div className={`result-card ${result.risk_level.toLowerCase()}`}>
                <div className="card-header">
                  <h3>RISK LEVEL: {result.risk_level}</h3>
                </div>
                <div className="stats-container">
                  <div className="stat-item">
                    <span>IP ADDRESS</span>
                    <strong>{result.source_ip}</strong>
                  </div>
                  <div className="stat-item">
                    <span>CONFIDENCE</span>
                    <strong>{result.threat_intel.abuse_confidence_score}%</strong>
                  </div>
                  <div className="stat-item">
                    <span>REPORTS</span>
                    <strong>{result.threat_intel.total_reports}</strong>
                  </div>
                  <div className="stat-item">
                    <span>ORIGIN</span>
                    <strong>{result.threat_intel.country_code || 'Unknown'}</strong>
                  </div>
                </div>
                <div className="icon-wrapper">
                  {getRiskIcon(result.risk_level)}
                </div>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;