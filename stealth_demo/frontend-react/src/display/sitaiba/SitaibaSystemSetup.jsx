import React, { useState, useEffect } from 'react'
import { Section, Button, Select, Output } from '../../components/common/index.jsx'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'
import { truncateHex } from '../../utils/helpers'

function SitaibaSystemSetup() {
  const { loadAllData, resetData } = useAppData()
  const [paramFiles, setParamFiles] = useState([])
  const [selectedParam, setSelectedParam] = useState('')
  const [loading, setLoading] = useState({})
  const [error, setError] = useState('')
  const [setupComplete, setSetupComplete] = useState(false)
  const [traceKey, setTraceKey] = useState(null)

  // Load parameter files list
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
      setTraceKey(data)
      setSetupComplete(true)
      
      // Load initial data after setup completion
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
      
      await resetData()
      setSetupComplete(false)
      setTraceKey(null)
      
    } catch (err) {
      setError('Reset failed: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, reset: false }))
    }
  }

  const getOutputContent = () => {
    if (error) {
      return `Error: ${error}`
    }
    
    if (setupComplete && traceKey) {
      return `✅ SITAIBA System Initialization Successful!
📄 Parameter File: ${selectedParam}
🔑 Tracer Public Key (TK): ${truncateHex(traceKey.TK_hex)}
🔐 Tracer Private Key (k): ${truncateHex(traceKey.k_hex)}
📊 G1 Group Size: ${traceKey.g1_size} bytes
📊 Zr Group Size: ${traceKey.zr_size} bytes
🎯 Scheme: ${traceKey.scheme}
✅ Status: ${traceKey.status}

`
    }
    
    return ''
  }

  return (
    <Section 
      title="🔧 System Setup (SITAIBA)" 
      statusActive={setupComplete}
    >
      <div className="controls">
        <label>Select Parameter File:</label>
        <Select
          value={selectedParam}
          onChange={(e) => setSelectedParam(e.target.value)}
          disabled={loading.paramFiles}
        >
          <option value="">
            {loading.paramFiles ? 'Loading...' : 'Select Parameter File...'}
          </option>
          {paramFiles.map((file) => (
            <option key={file.name} value={file.name}>
              {file.name} ({file.size} bytes)
            </option>
          ))}
        </Select>
        
        <div className="inline-controls">
          <Button
            onClick={handleSetup}
            loading={loading.setup}
            disabled={!selectedParam || loading.setup}
          >
            Initialize SITAIBA System
          </Button>
          
          <Button
            onClick={handleReset}
            variant="secondary"
            loading={loading.reset}
            disabled={loading.reset}
          >
            Reset System
          </Button>
        </div>
      </div>
      
      <Output 
        content={getOutputContent()}
        isError={!!error}
      />
    </Section>
  )
}

export default SitaibaSystemSetup