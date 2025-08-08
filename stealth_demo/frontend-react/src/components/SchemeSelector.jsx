import React, { useState, useEffect } from 'react'
import { Card, Button, Select } from './common'

export default function SchemeSelector() {
  const [schemes, setSchemes] = useState([])
  const [currentScheme, setCurrentScheme] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Load available schemes on component mount
  useEffect(() => {
    loadSchemes()
  }, [])

  const loadSchemes = async () => {
    try {
      const baseUrl = window.location.hostname === 'localhost' && window.location.port === '5173' 
        ? 'http://localhost:3000'  // Vite開發模式
        : '';  // 生產模式
      const response = await fetch(`${baseUrl}/schemes`)
      const data = await response.json()
      setSchemes(data.schemes || [])
      setCurrentScheme(data.current)
    } catch (error) {
      console.error('Failed to load schemes:', error)
      setError('Failed to load available schemes')
    }
  }

  const handleSchemeChange = async (schemeId) => {
    if (schemeId === currentScheme?.id) return
    
    setLoading(true)
    setError('')

    try {
      const baseUrl = window.location.hostname === 'localhost' && window.location.port === '5173' 
        ? 'http://localhost:3000'  // Vite開發模式
        : '';  // 生產模式
      const response = await fetch(`${baseUrl}/schemes/${schemeId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      const result = await response.json()
      
      if (response.ok) {
        setCurrentScheme(result.scheme)
        // Trigger a custom event to notify other components about scheme change
        window.dispatchEvent(new CustomEvent('schemeChanged', { 
          detail: { scheme: result.scheme } 
        }))
      } else {
        setError(result.error || 'Failed to switch scheme')
      }
    } catch (error) {
      console.error('Scheme switch error:', error)
      setError('Failed to switch scheme')
    } finally {
      setLoading(false)
    }
  }

  const getSchemeStatusBadge = (scheme) => {
    if (!scheme.available) {
      return <span className="badge badge-unavailable">❌ Unavailable</span>
    }
    if (currentScheme?.id === scheme.id) {
      return <span className="badge badge-active">✅ Active</span>
    }
    return <span className="badge badge-ready">📁 Ready</span>
  }

  const getFunctionSupportList = (functions) => {
    const functionDescriptions = {
      init: '🔧 Initialize',
      keygen: '🔑 Key Generation',
      tracekeygen: '🔍 Trace Key Gen',
      addr_gen: '📍 Address Generation', 
      addr_verify: '✓ Address Verification',
      dsk_gen: '🎫 DSK Generation',
      sign: '✍️ Message Signing',
      verify: '🔍 Signature Verification',
      trace: '🕵️ Identity Tracing',
      performance: '⚡ Performance Testing'
    }

    return functions.map(func => functionDescriptions[func] || func).join(', ')
  }

  return (
    <Card title="🎯 Cryptographic Scheme Selection" className="scheme-selector">
      {error && <div className="error">{error}</div>}
      
      {/* Current Scheme Display */}
      {currentScheme && (
        <div className="current-scheme">
          <h4>Current Scheme: {currentScheme.name}</h4>
          <p className="description">{currentScheme.description}</p>
          <div className="scheme-details">
            <span className="param-type">
              📋 Parameters: {currentScheme.param_type?.toUpperCase()}
            </span>
            <span className="functions">
              🔧 Functions: {getFunctionSupportList(currentScheme.functions)}
            </span>
          </div>
        </div>
      )}

      {/* Scheme Selection */}
      <div className="scheme-grid">
        {schemes.map(scheme => (
          <div key={scheme.id} className={`scheme-card ${currentScheme?.id === scheme.id ? 'active' : ''}`}>
            <div className="scheme-header">
              <h4>{scheme.name}</h4>
              {getSchemeStatusBadge(scheme)}
            </div>
            
            <p className="scheme-description">{scheme.description}</p>
            
            <div className="scheme-info">
              <div className="info-item">
                <strong>Parameters:</strong> {scheme.param_type?.toUpperCase()}
              </div>
              <div className="info-item">
                <strong>Functions:</strong> {scheme.functions?.length || 0}
              </div>
            </div>

            <div className="function-list">
              {getFunctionSupportList(scheme.functions || [])}
            </div>

            <Button
              onClick={() => handleSchemeChange(scheme.id)}
              disabled={!scheme.available || loading || currentScheme?.id === scheme.id}
              variant={currentScheme?.id === scheme.id ? 'primary' : 'secondary'}
              className="select-scheme-btn"
            >
              {loading && currentScheme?.id !== scheme.id ? 
                '⏳ Switching...' : 
                currentScheme?.id === scheme.id ? 
                '✅ Current' : 
                scheme.available ? 
                '🔄 Select' : 
                '❌ N/A'
              }
            </Button>
          </div>
        ))}
      </div>

      {/* Help Text */}
      <div className="help-text">
        <p>
          💡 <strong>How to use:</strong> Select a cryptographic scheme to begin. 
          Each scheme supports different cryptographic operations. 
          Available schemes are shown with a ✅ ready status.
        </p>
        <p>
          🔄 <strong>Note:</strong> Switching schemes will clear all existing data 
          (keys, addresses, signatures) and require re-initialization.
        </p>
      </div>
    </Card>
  )
}

// CSS Styles (add to App.css)
const styles = `
.scheme-selector .current-scheme {
  background: #e8f5e8;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  border: 2px solid #4CAF50;
}

.scheme-selector .current-scheme h4 {
  margin: 0 0 0.5rem 0;
  color: #2E7D32;
}

.scheme-selector .scheme-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.9rem;
}

.scheme-selector .scheme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.scheme-selector .scheme-card {
  border: 2px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  background: white;
  transition: all 0.2s ease;
}

.scheme-selector .scheme-card:hover {
  border-color: #4CAF50;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.scheme-selector .scheme-card.active {
  border-color: #4CAF50;
  background: #f8fff8;
}

.scheme-selector .scheme-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.scheme-selector .scheme-header h4 {
  margin: 0;
}

.scheme-selector .badge {
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.scheme-selector .badge-active {
  background: #4CAF50;
  color: white;
}

.scheme-selector .badge-ready {
  background: #2196F3;
  color: white;
}

.scheme-selector .badge-unavailable {
  background: #f44336;
  color: white;
}

.scheme-selector .scheme-description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.scheme-selector .scheme-info {
  margin-bottom: 0.5rem;
}

.scheme-selector .info-item {
  font-size: 0.85rem;
  color: #555;
}

.scheme-selector .function-list {
  font-size: 0.8rem;
  color: #777;
  margin-bottom: 1rem;
  min-height: 2rem;
}

.scheme-selector .select-scheme-btn {
  width: 100%;
}

.scheme-selector .help-text {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  margin-top: 1rem;
}

.scheme-selector .help-text p {
  margin: 0.5rem 0;
}
`