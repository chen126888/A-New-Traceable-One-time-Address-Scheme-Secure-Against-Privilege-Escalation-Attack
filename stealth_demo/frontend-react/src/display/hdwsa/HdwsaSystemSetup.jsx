import React, { useState, useEffect } from 'react'
import { Section, Button, Select, Output } from '../../components/common/index.jsx'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'
import { truncateHex } from '../../utils/helpers'

function HdwsaSystemSetup() {
  const { loadAllData, resetData } = useAppData()
  const [paramFiles, setParamFiles] = useState([])
  const [selectedParam, setSelectedParam] = useState('')
  const [loading, setLoading] = useState({})
  const [error, setError] = useState('')
  const [setupComplete, setSetupComplete] = useState(false)
  const [rootWallet, setRootWallet] = useState(null)

  // 載入參數文件列表
  useEffect(() => {
    loadParamFiles()
  }, [])

  const loadParamFiles = async () => {
    try {
      setLoading(prev => ({ ...prev, paramFiles: true }))
      const data = await apiService.getParamFiles()
      setParamFiles(data.param_files)
      if (data.current) {
        setSelectedParam(data.current)
      }
    } catch (err) {
      setError('Failed to load parameter files: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, paramFiles: false }))
    }
  }

  const handleSetup = async () => {
    if (!selectedParam) {
      setError('Please select a parameter file')
      return
    }

    try {
      setLoading(prev => ({ ...prev, setup: true }))
      setError('')
      
      const data = await apiService.setup(selectedParam)
      setRootWallet(data)
      setSetupComplete(true)
      
      // 載入所有數據
      await loadAllData()
    } catch (err) {
      setError('Setup failed: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, setup: false }))
    }
  }

  const handleReset = async () => {
    try {
      setLoading(prev => ({ ...prev, reset: true }))
      setError('')
      
      await apiService.reset()
      
      // 清除狀態
      setSetupComplete(false)
      setRootWallet(null)
      setSelectedParam('')
      
      // 重設數據
      resetData()
      
    } catch (err) {
      setError('Reset failed: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, reset: false }))
    }
  }

  return (
    <Section 
      title="🔧 HDWSA System Setup"
      statusActive={setupComplete}
    >
      
      <Section title="Parameter File Selection">
        <div className="setup-controls">
          <Select
            label="Parameter File:"
            value={selectedParam}
            onChange={(e) => setSelectedParam(e.target.value)}
            disabled={loading.paramFiles || setupComplete}
            loading={loading.paramFiles}
          >
            <option value="">Select parameter file...</option>
            {paramFiles.map(file => (
              <option key={file.name} value={file.name}>
                {file.name} ({(file.size / 1024).toFixed(1)} KB)
              </option>
            ))}
          </Select>

          <div className="action-buttons">
            <Button
              onClick={handleSetup}
              loading={loading.setup}
              disabled={!selectedParam || setupComplete}
              variant="primary"
            >
              🚀 Initialize System
            </Button>
            
            

            {setupComplete && (
              <Button
                onClick={handleReset}
                loading={loading.reset}
                variant="danger"
              >
                🔄 Reset System
              </Button>
            )}
          </div>
        </div>
      </Section>

      {error && (
        <Section title="⚠️ Error">
          <div className="error-message">{error}</div>
        </Section>
      )}

      {setupComplete && rootWallet && (
        <Section title="✅ HDWSA Root Wallet Generated">
          <div className="root-wallet-info">
            <div className="status-message">
              🎉 HDWSA system successfully initialized with hierarchical wallet support!
            </div>
            
            <div className="wallet-details">
              <h4>🏠 Root Wallet Information</h4>
              <div className="key-grid">
                <div className="key-item">
                  <strong>📄 Parameter File:</strong>
                  <span className="param-name">{rootWallet.param_file}</span>
                </div>
                
                <div className="key-item">
                  <strong>🔑 Root Public Key A:</strong>
                  <span className="key-value">{truncateHex(rootWallet.root_A_hex, 20)}</span>
                </div>
                
                <div className="key-item">
                  <strong>🔑 Root Public Key B:</strong>
                  <span className="key-value">{truncateHex(rootWallet.root_B_hex, 20)}</span>
                </div>
                
                <div className="key-item">
                  <strong>📏 Element Sizes:</strong>
                  <span className="element-sizes">
                    G1: {rootWallet.g1_size}B, Zr: {rootWallet.zr_size}B, GT: {rootWallet.gt_size}B
                  </span>
                </div>
              </div>

              
            </div>
          </div>
        </Section>
      )}

    </Section>
  )
}

export default HdwsaSystemSetup
