import React, { useState, useCallback } from 'react'
import { Section, Button, Select, DataList, Output } from '../../components/common'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'
import { truncateHex } from '../../utils/helpers'

function StealthIdentityTracing() {
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
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (selectedTraceIndex >= 0 && traceResults[selectedTraceIndex]) {
      const trace = traceResults[selectedTraceIndex]
      const matchedKey = findMatchingKey(trace.recovered_b_hex)
      const inputAddr = trace.input_address
      
      return `🔍 Identity Tracing Results - Trace ${selectedTraceIndex}
📧 Traced Address: ${trace.address_id}
⏰ Traced at: ${trace.timestamp}
📊 Status: ${trace.status}

🔐 Recovered Identity:
B (Public Key): ${trace.recovered_b_hex}

📋 Original Address Information:
🏠 Address: ${inputAddr?.addr_hex}
🎲 R1: ${inputAddr?.r1_hex}
🎲 R2: ${inputAddr?.r2_hex}
🔒 C: ${inputAddr?.c_hex}
👤 Claimed Owner: ${inputAddr?.key_id}

🔍 Trace Authority Analysis:
${trace.original_owner ? `
🎯 Original Owner Record:
   Key Index: ${trace.original_owner.key_index}
   Key ID: ${trace.original_owner.key_id}
   B_hex: ${trace.original_owner.B_hex}
` : ''}

🤝 Key Matching Results:
${matchedKey ? `
✅ IDENTITY CONFIRMED!
   Matched Key: ${matchedKey.id}
   Key Index: ${keys.indexOf(matchedKey)}
   Perfect Match: ${matchedKey.B_hex === trace.recovered_b_hex ? 'YES' : 'NO'}
` : `
⚠️ No matching key found in current key list
   This could mean:
   - Key was generated elsewhere
   - Key was deleted from the system
   - Address was created with external keys
`}

🔄 Perfect Match Status: ${trace.perfect_match ? '✅ YES' : '❌ NO'}
📊 Tracing Status: ${trace.status}`
    }
    
    // 顯示最新追蹤結果
    if (traceResults.length > 0) {
      const latestTrace = traceResults[traceResults.length - 1]
      const matchedKey = findMatchingKey(latestTrace.recovered_b_hex)
      
      return `✅ Identity Tracing Completed!
📧 Traced Address: ${latestTrace.address_id}
🔐 Recovered B: ${truncateHex(latestTrace.recovered_b_hex)}
🤝 Match Found: ${matchedKey ? `YES (${matchedKey.id})` : 'NO'}
🔄 Perfect Match: ${latestTrace.perfect_match ? 'YES' : 'NO'}
📊 Status: ${latestTrace.status}`
    }
    
    return 'Select an address to trace its identity...'
  }

  const traceItems = traceResults.map((trace, index) => {
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

  const calculateSuccessRate = () => {
    if (traceResults.length === 0) return 0
    return Math.round((traceResults.filter(t => t.perfect_match).length / traceResults.length) * 100)
  }

  return (
    <Section title="🔍 Identity Tracing (Stealth)">
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
      
      <DataList items={traceItems} />
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />
    </Section>
  )
}

export default StealthIdentityTracing