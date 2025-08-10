import React from 'react';

const SitaibaPerformanceDisplay = ({ data }) => {
  if (!data) return null;

  const formatTime = (time) => {
    if (time === null || time === undefined) return 'N/A';
    return `${time.toFixed(3)}ms`;
  };

  return (
    <div className="performance-results">
      <h4>🚀 SITAIBA Performance Results</h4>
      <div className="performance-summary">
        <p><strong>Iterations:</strong> {data.iterations}</p>
        <p><strong>Status:</strong> ✅ {data.status}</p>
        <p><em>{data.note}</em></p>
      </div>
      
      <div className="performance-metrics">
        <div className="metric-row">
          <span className="metric-name">🏠 Address Generation:</span>
          <span className="metric-value">{formatTime(data.addr_gen_ms)}</span>
        </div>
        
        <div className="metric-row">
          <span className="metric-name">🔍 Address Verification:</span>
          <span className="metric-value">{formatTime(data.addr_verify_ms)}</span>
        </div>
        
        <div className="metric-row">
          <span className="metric-name">⚡ Fast Address Verification:</span>
          <span className="metric-value">{formatTime(data.fast_verify_ms)}</span>
        </div>
        
        <div className="metric-row">
          <span className="metric-name">🔑 One-time Secret Key Gen:</span>
          <span className="metric-value">{formatTime(data.onetime_sk_ms)}</span>
        </div>
        
        <div className="metric-row">
          <span className="metric-name">🕵️ Identity Tracing:</span>
          <span className="metric-value">{formatTime(data.trace_ms)}</span>
        </div>
      </div>

      <div className="performance-chart">
        <h5>📊 Operation Time Comparison</h5>
        <div className="chart-bars">
          <div className="bar-container">
            <div className="bar-label">Addr Gen</div>
            <div className="bar-wrapper">
              <div 
                className="bar addr-gen" 
                style={{width: `${Math.min((data.addr_gen_ms / Math.max(data.addr_gen_ms, data.addr_verify_ms, data.fast_verify_ms, data.onetime_sk_ms, data.trace_ms)) * 100, 100)}%`}}
              ></div>
              <span className="bar-value">{formatTime(data.addr_gen_ms)}</span>
            </div>
          </div>
          
          <div className="bar-container">
            <div className="bar-label">Addr Verify</div>
            <div className="bar-wrapper">
              <div 
                className="bar addr-verify" 
                style={{width: `${Math.min((data.addr_verify_ms / Math.max(data.addr_gen_ms, data.addr_verify_ms, data.fast_verify_ms, data.onetime_sk_ms, data.trace_ms)) * 100, 100)}%`}}
              ></div>
              <span className="bar-value">{formatTime(data.addr_verify_ms)}</span>
            </div>
          </div>
          
          <div className="bar-container">
            <div className="bar-label">Fast Verify</div>
            <div className="bar-wrapper">
              <div 
                className="bar fast-verify" 
                style={{width: `${Math.min((data.fast_verify_ms / Math.max(data.addr_gen_ms, data.addr_verify_ms, data.fast_verify_ms, data.onetime_sk_ms, data.trace_ms)) * 100, 100)}%`}}
              ></div>
              <span className="bar-value">{formatTime(data.fast_verify_ms)}</span>
            </div>
          </div>
          
          <div className="bar-container">
            <div className="bar-label">DSK Gen</div>
            <div className="bar-wrapper">
              <div 
                className="bar dsk-gen" 
                style={{width: `${Math.min((data.onetime_sk_ms / Math.max(data.addr_gen_ms, data.addr_verify_ms, data.fast_verify_ms, data.onetime_sk_ms, data.trace_ms)) * 100, 100)}%`}}
              ></div>
              <span className="bar-value">{formatTime(data.onetime_sk_ms)}</span>
            </div>
          </div>
          
          <div className="bar-container">
            <div className="bar-label">Tracing</div>
            <div className="bar-wrapper">
              <div 
                className="bar trace" 
                style={{width: `${Math.min((data.trace_ms / Math.max(data.addr_gen_ms, data.addr_verify_ms, data.fast_verify_ms, data.onetime_sk_ms, data.trace_ms)) * 100, 100)}%`}}
              ></div>
              <span className="bar-value">{formatTime(data.trace_ms)}</span>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .performance-results {
          background: #f8f9fa;
          border: 1px solid #e9ecef;
          border-radius: 8px;
          padding: 15px;
          margin: 10px 0;
        }

        .performance-summary {
          margin-bottom: 15px;
          padding-bottom: 10px;
          border-bottom: 1px solid #dee2e6;
        }

        .performance-summary p {
          margin: 5px 0;
        }

        .performance-metrics {
          margin-bottom: 20px;
        }

        .metric-row {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid #f1f3f4;
        }

        .metric-row:last-child {
          border-bottom: none;
        }

        .metric-name {
          font-weight: 500;
          color: #495057;
        }

        .metric-value {
          font-family: 'Courier New', monospace;
          font-weight: bold;
          color: #007bff;
        }

        .performance-chart h5 {
          margin-bottom: 15px;
          color: #343a40;
        }

        .bar-container {
          margin-bottom: 10px;
        }

        .bar-label {
          font-size: 12px;
          font-weight: 500;
          margin-bottom: 4px;
          color: #6c757d;
        }

        .bar-wrapper {
          display: flex;
          align-items: center;
          height: 24px;
        }

        .bar {
          height: 100%;
          min-width: 2px;
          border-radius: 3px;
          margin-right: 8px;
          transition: width 0.3s ease;
        }

        .bar.addr-gen {
          background: linear-gradient(90deg, #007bff, #0056b3);
        }

        .bar.addr-verify {
          background: linear-gradient(90deg, #28a745, #1e7e34);
        }

        .bar.fast-verify {
          background: linear-gradient(90deg, #ffc107, #e0a800);
        }

        .bar.dsk-gen {
          background: linear-gradient(90deg, #17a2b8, #117a8b);
        }

        .bar.trace {
          background: linear-gradient(90deg, #dc3545, #c82333);
        }

        .bar-value {
          font-family: 'Courier New', monospace;
          font-size: 11px;
          font-weight: bold;
          color: #495057;
        }
      `}</style>
    </div>
  );
};

export default SitaibaPerformanceDisplay;