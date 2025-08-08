import React, { useState, useEffect } from 'react'
import { Section, Button, Select, Output } from './common/index.jsx'
import { apiService } from '../services/apiService'
import { useAppData } from '../hooks/useAppData'
import { truncateHex } from '../utils/helpers'

function SystemSetup() {
  const { loadAllData, resetData } = useAppData()
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

  // 監聽方案變更事件
  useEffect(() => {
    const handleSchemeChange = () => {
      // 方案變更時重新加載參數文件
      loadParamFiles()
      // 重置設置狀態
      setSetupComplete(false)
      setSelectedParam('')
      setError('')
    }

    window.addEventListener('schemeChanged', handleSchemeChange)
    return () => window.removeEventListener('schemeChanged', handleSchemeChange)
  }, [])

  const loadParamFiles = async () => {
    try {
      setLoading(prev => ({ ...prev, paramFiles: true }))
      setError('') // 清除之前的錯誤
      
      const data = await apiService.getParamFiles()
      setParamFiles(data.param_files)
      if (data.current) {
        setSelectedParam(data.current)
      }
    } catch (err) {
      // 如果是 "No scheme selected" 錯誤，不顯示為錯誤狀態
      if (err.message.includes('No scheme selected')) {
        console.log('Waiting for scheme selection...')
        setParamFiles([])
        setSelectedParam('')
      } else {
        setError('Failed to load parameter files: ' + err.message)
      }
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
      
      // 設置完成後載入初始數據
      await loadAllData()
      
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
    
    if (setupComplete) {
      let output = `✅ System Initialized Successfully!
📄 Parameter File: ${selectedParam}`;
      
      if (traceKey) {
        output += `
🔑 Trace Key: ${truncateHex(traceKey.TK_hex || '')}
🔐 K Value: ${truncateHex(traceKey.k_hex || '')}
📊 G1 Size: ${traceKey.g1_size || 'N/A'} bytes
📊 Zr Size: ${traceKey.zr_size || 'N/A'} bytes`;
      }
      
      output += `
✅ Status: ${traceKey?.status || 'success'}`;
      
      return output
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
            {loading.paramFiles ? 'Loading...' : 
             paramFiles.length === 0 ? 'Please select a scheme first...' : 
             'Select a parameter file...'}
          </option>
          {paramFiles.map((file) => (
            <option key={file} value={file}>
              {file}
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