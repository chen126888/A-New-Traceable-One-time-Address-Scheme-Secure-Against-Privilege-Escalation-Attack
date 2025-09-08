import React from 'react'
import { useSchemeContext } from '../hooks/useSchemeContext'

function SchemeSelector() {
  const { 
    currentScheme, 
    availableSchemes, 
    capabilities,
    loading,
    switchScheme,
    clearCurrentData,
    clearAllData
  } = useSchemeContext()

  const handleSchemeChange = async (e) => {
    const newScheme = e.target.value
    if (newScheme !== currentScheme) {
      const success = await switchScheme(newScheme)
      if (!success) {
        // 如果切換失败，重置選擇器
        e.target.value = currentScheme
      }
    }
  }

  const getSchemeDisplayName = (scheme) => {
    const names = {
      'stealth': 'Stealth',
      'sitaiba': 'Sitaiba'
    }
    return names[scheme] || scheme
  }

  const getSchemeBadge = (scheme) => {
    if (scheme === 'stealth') {
      return <span className="badge implemented">Implemented</span>
    } else if (scheme === 'sitaiba') {
      return <span className="badge implemented">Implemented</span>
    }
    return null
  }

  return (
    <div className="card">
      <h3>🔄 Cryptography Scheme Selection</h3>
      
      <div className="scheme-selector">
        <div className="select-group">
          <label>Select Scheme:</label>
          <select 
            value={currentScheme} 
            onChange={handleSchemeChange}
            disabled={loading}
            className={loading ? 'loading' : ''}
          >
            {availableSchemes.map(scheme => (
              <option key={scheme} value={scheme}>
                {getSchemeDisplayName(scheme)}
              </option>
            ))}
          </select>
          {loading && <span className="loading-spinner">🔄</span>}
        </div>

        <div className="current-scheme">
          <div className="scheme-info">
            <div className="scheme-name">
              Current Scheme: <strong>{currentScheme}</strong>
              {getSchemeBadge(currentScheme)}
            </div>
            
            <div className="scheme-capabilities">
              <h4>Supported Features:</h4>
              <div className="capabilities-list">
                <span className={capabilities.has_setup ? 'enabled' : 'disabled'}>
                  {capabilities.has_setup ? '✅' : '❌'} System Setup
                </span>
                <span className={capabilities.has_keygen ? 'enabled' : 'disabled'}>
                  {capabilities.has_keygen ? '✅' : '❌'} Key Generation
                </span>
                <span className={capabilities.has_addrgen ? 'enabled' : 'disabled'}>
                  {capabilities.has_addrgen ? '✅' : '❌'} Address Generation
                </span>
                <span className={capabilities.has_dskgen ? 'enabled' : 'disabled'}>
                  {capabilities.has_dskgen ? '✅' : '❌'} DSK Generation
                </span>
                <span className={capabilities.has_signing ? 'enabled' : 'disabled'}>
                  {capabilities.has_signing ? '✅' : '❌'} Message Signing
                </span>
                <span className={capabilities.has_verification ? 'enabled' : 'disabled'}>
                  {capabilities.has_verification ? '✅' : '❌'} Signature Verification
                </span>
                <span className={capabilities.has_tracing ? 'enabled' : 'disabled'}>
                  {capabilities.has_tracing ? '✅' : '❌'} Identity Tracing
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="scheme-actions">
          <button 
            onClick={clearAllData}
            className="btn-danger"
            title="Clear data for all schemes"
          >
            🗑️ Clear All Data
          </button>
        </div>
      </div>

      <style>{`
        .scheme-selector {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .select-group {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .select-group label {
          font-weight: bold;
          min-width: 80px;
        }

        .select-group select {
          flex: 1;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }

        .select-group select.loading {
          opacity: 0.7;
        }

        .loading-spinner {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .current-scheme {
          background: #f5f5f5;
          padding: 1rem;
          border-radius: 4px;
          border-left: 4px solid #007bff;
        }

        .scheme-name {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
          font-size: 16px;
        }

        .badge {
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 11px;
          font-weight: bold;
          text-transform: uppercase;
        }

        .badge.implemented {
          background: #28a745;
          color: white;
        }

        .badge.placeholder {
          background: #ffc107;
          color: #212529;
        }

        .capabilities-list {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
          gap: 0.25rem;
          margin-top: 0.5rem;
        }

        .capabilities-list span {
          font-size: 12px;
          padding: 2px 4px;
        }

        .capabilities-list .enabled {
          color: #28a745;
        }

        .capabilities-list .disabled {
          color: #dc3545;
        }

        .scheme-actions {
          display: flex;
          gap: 0.5rem;
        }

        .scheme-actions button {
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-danger {
          background: #dc3545;
          color: white;
        }

        .scheme-actions button:hover {
          opacity: 0.8;
        }

        h4 {
          margin: 0.5rem 0 0.25rem 0;
          font-size: 14px;
          color: #666;
        }
      `}</style>
    </div>
  )
}

export default SchemeSelector