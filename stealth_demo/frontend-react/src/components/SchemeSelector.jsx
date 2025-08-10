import React, { useState, useEffect } from 'react'
import { Section, Button, Select, Output } from './common/index.jsx'
import { apiService } from '../services/apiService'

function SchemeSelector({ onSchemeChange }) {
  const [schemes, setSchemes] = useState([])
  const [activeScheme, setActiveScheme] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Load available schemes on component mount
  useEffect(() => {
    loadSchemes()
  }, [])

  const loadSchemes = async () => {
    try {
      setLoading(true)
      const data = await apiService.get('/schemes')
      setSchemes(data.schemes)
      setActiveScheme(data.active_scheme)
      if (onSchemeChange) {
        onSchemeChange(data.active_scheme)
      }
    } catch (err) {
      setError('Failed to load schemes: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSchemeChange = async (schemeName) => {
    if (!schemeName || schemeName === activeScheme) return

    try {
      setLoading(true)
      setError('')
      
      await apiService.post('/schemes/activate', { 
        scheme_name: schemeName 
      })
      
      setActiveScheme(schemeName)
      if (onSchemeChange) {
        onSchemeChange(schemeName)
      }
      
      // Force reload of the page data after scheme change
      window.location.reload()
      
    } catch (err) {
      setError('Failed to activate scheme: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading && schemes.length === 0) {
    return (
      <Section title="Cryptographic Scheme">
        <div>Loading schemes...</div>
      </Section>
    )
  }

  return (
    <Section title="Cryptographic Scheme">
      <div className="space-y-4">
        {error && (
          <div className="text-red-500 text-sm">{error}</div>
        )}
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Cryptographic Scheme:
          </label>
          <Select 
            value={activeScheme}
            onChange={(e) => handleSchemeChange(e.target.value)}
            disabled={loading}
            className="w-full"
          >
            <option value="">Select a scheme...</option>
            {schemes.map(scheme => (
              <option key={scheme.name} value={scheme.name}>
                {scheme.name} v{scheme.version} - {scheme.description}
              </option>
            ))}
          </Select>
        </div>

        {activeScheme && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-2">Active Scheme: {activeScheme}</h4>
            {schemes.find(s => s.name === activeScheme) && (
              <div className="text-sm text-gray-600 space-y-1">
                <div><strong>Version:</strong> {schemes.find(s => s.name === activeScheme).version}</div>
                <div><strong>Author:</strong> {schemes.find(s => s.name === activeScheme).author}</div>
                <div><strong>Capabilities:</strong> {schemes.find(s => s.name === activeScheme).capabilities.join(', ')}</div>
                <div><strong>Description:</strong> {schemes.find(s => s.name === activeScheme).description}</div>
              </div>
            )}
          </div>
        )}

        {loading && (
          <div className="text-blue-500 text-sm">
            {activeScheme ? 'Switching scheme...' : 'Loading schemes...'}
          </div>
        )}
      </div>
    </Section>
  )
}

export default SchemeSelector