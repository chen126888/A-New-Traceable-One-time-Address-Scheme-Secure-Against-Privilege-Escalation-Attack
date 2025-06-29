import React, { useState, useEffect } from 'react'
import { Section, Button, Select, Output } from './common/index.jsx'
import { apiService } from '../services/apiService'
import { truncateHex } from '../utils/helpers'

function SystemSetup() {
  const [paramFiles, setParamFiles] = useState([])
  const [selectedParam, setSelectedParam] = useState('')
  const [loading, setLoading] = useState({})
  const [error, setError] = useState('')
  const [setupComplete, setSetupComplete] = useState(false)
  const [traceKey, setTraceKey] = useState(null)

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
      setTraceKey(data)
      setSetupComplete(true)
      
    } catch (err) {
      setError('Setup failed: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, setup: false }))
    }
  }

  const getOutputContent = () => {
    if (error) {
      return `Error: ${error}`
    }
    
    if (setupComplete && traceKey) {
      return `✅ System Initialized Successfully!
📄 Parameter File: ${selectedParam}
🔑 Trace Key: ${truncateHex(traceKey.TK_hex)}
🔐 K Value: ${truncateHex(traceKey.k_hex)}
📊 G1 Size: ${traceKey.g1_size} bytes
📊 Zr Size: ${traceKey.zr_size} bytes
✅ Status: ${traceKey.status}`
    }
    
    return ''
  }

  return (
    <Section 
      title="🔧 System Setup" 
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
            {loading.paramFiles ? 'Loading...' : 'Select a parameter file...'}
          </option>
          {paramFiles.map((file) => (
            <option key={file.name} value={file.name}>
              {file.name} ({file.size} bytes)
            </option>
          ))}
        </Select>
        
        <Button
          onClick={handleSetup}
          loading={loading.setup}
          disabled={!selectedParam || loading.setup}
        >
          Initialize with Selected Param
        </Button>
      </div>
      
      <Output 
        content={getOutputContent()}
        isError={!!error}
      />
    </Section>
  )
}

export default SystemSetup