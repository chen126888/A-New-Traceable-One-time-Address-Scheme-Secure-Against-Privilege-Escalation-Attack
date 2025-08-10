import React, { useState, useCallback } from 'react'
import { Section, Button, Select, DataList, Output } from './common'
import { apiService } from '../services/apiService'
import { useAppData } from '../hooks/useAppData'
import { truncateHex } from '../utils/helpers'
import { getDisplayComponent } from './displays'

function IdentityTracing({ activeScheme }) {
  const { 
    keys,
    addresses, 
    loading: globalLoading, 
    error: globalError, 
    clearError,
    loadKeys,
    loadAddresses
  } = useAppData()
  
  const [selectedAddrIndex, setSelectedAddrIndex] = useState('')
  const [selectedTraceIndex, setSelectedTraceIndex] = useState(-1)
  const [traceResults, setTraceResults] = useState([])
  const [localLoading, setLocalLoading] = useState({})
  const [localError, setLocalError] = useState('')

  // 刷新數據
  const handleRefreshData = useCallback(async () => {
    setLocalError('')
    clearError()
    await Promise.all([loadKeys(), loadAddresses()])
  }, [loadKeys, loadAddresses, clearError])

  // 執行身份追蹤
  const handleTraceIdentity = useCallback(async () => {
    if (selectedAddrIndex === '') {
      setLocalError('Please select an address to trace!')
      return
    }

    try {
      setLocalLoading(prev => ({ ...prev, tracing: true }))
      setLocalError('')
      clearError()
      
      const result = await apiService.traceIdentity(parseInt(selectedAddrIndex))
      
      const traceWithIndex = {
        ...result,
        index: traceResults.length,
        timestamp: new Date().toISOString(),
        input_address: addresses[parseInt(selectedAddrIndex)]
      }
      
      setTraceResults(prev => [...prev, traceWithIndex])
      
    } catch (err) {
      setLocalError('Identity tracing failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, tracing: false }))
    }
  }, [selectedAddrIndex, addresses, traceResults.length, clearError])

  // 點擊追蹤結果項目
  const handleTraceClick = useCallback((index) => {
    setSelectedTraceIndex(index)
  }, [])

  // 查找匹配的密鑰
  const findMatchingKey = useCallback((recoveredBHex) => {
    return keys.find(key => key.B_hex === recoveredBHex)
  }, [keys])

  const getOutputContent = () => {
    // 使用 scheme-specific 的 Display 組件
    const TraceDisplay = getDisplayComponent(activeScheme, 'TraceDisplay')
    if (TraceDisplay) {
      return TraceDisplay({
        traceResults,
        selectedTraceIndex,
        keys,
        findMatchingKey,
        localError,
        globalError
      })
    }
    
    // fallback to default display
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (traceResults.length > 0) {
      const latestTrace = traceResults[traceResults.length - 1]
      const matchedKey = findMatchingKey(latestTrace.recovered_b_hex)
      
      return `✅ Identity Tracing Completed!
📧 Traced Address: ${latestTrace.address_id}
🔐 Recovered B: ${truncateHex(latestTrace.recovered_b_hex)}
🤝 Match Found: ${matchedKey ? `YES (${matchedKey.id})` : 'NO'}`
    }
    
    return 'Select an address to trace its identity...'
  }

  const getTraceItems = () => {
    // 使用 scheme-specific 的 List Items 組件
    const TraceListItems = getDisplayComponent(activeScheme, 'TraceListItems')
    if (TraceListItems) {
      return TraceListItems({
        traceResults,
        selectedTraceIndex,
        onTraceClick: handleTraceClick,
        findMatchingKey
      })
    }
    
    // fallback to default items
    return traceResults.map((trace, index) => {
      const matchedKey = findMatchingKey(trace.recovered_b_hex)
      return {
        id: `trace_${index}`,
        header: `Trace ${index} (${trace.address_id})`,
        details: [
          `Recovered B: ${truncateHex(trace.recovered_b_hex, 12)}`,
          `Match: ${matchedKey ? matchedKey.id : 'None'}`,
          `Status: ${trace.perfect_match ? 'Perfect' : 'Partial'}`
        ],
        selected: index === selectedTraceIndex,
        onClick: () => handleTraceClick(index)
      }
    })
  }

  const calculateSuccessRate = () => {
    if (traceResults.length === 0) return 0
    return Math.round((traceResults.filter(t => t.perfect_match).length / traceResults.length) * 100)
  }

  return (
    <Section title="🔍 Identity Tracing">
      <div className="controls">
        <label>Select Address to Trace:</label>
        <Select
          value={selectedAddrIndex}
          onChange={(e) => setSelectedAddrIndex(e.target.value)}
        >
          <option value="">Select an address to trace...</option>
          {addresses.map((addr, index) => (
            <option key={addr.id} value={index}>
              {addr.id} - Owner: {addr.key_id} - {truncateHex(addr.addr_hex, 8)}
            </option>
          ))}
        </Select>
        
        <div className="inline-controls">
          <Button
            onClick={handleTraceIdentity}
            loading={localLoading.tracing}
            disabled={selectedAddrIndex === '' || localLoading.tracing}
          >
            Trace Identity
          </Button>
          
          <Button
            onClick={handleRefreshData}
            variant="secondary"
          >
            Refresh Data
          </Button>
        </div>
        
        {traceResults.length > 0 && (
          <div className="trace-summary">
            <strong>Trace Authority Status: Active</strong>
            <div>Total Traces Performed: {traceResults.length}</div>
            <div>Success Rate: {calculateSuccessRate()}%</div>
          </div>
        )}
      </div>
      
      <DataList items={getTraceItems()} />
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />
    </Section>
  )
}

export default IdentityTracing