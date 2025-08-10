import React, { useState, useCallback } from 'react'
import { Section, Button, Input, Output } from './common'
import { apiService } from '../services/apiService'
import { useAppData } from '../hooks/useAppData'
import SitaibaPerformanceDisplay from './displays/SitaibaPerformanceDisplay'

function PerformanceTest() {
  const { 
    loading: globalLoading, 
    error: globalError, 
    clearError
  } = useAppData()
  
  const [iterations, setIterations] = useState(100)
  const [testResults, setTestResults] = useState([])
  const [selectedResultIndex, setSelectedResultIndex] = useState(-1)
  const [localLoading, setLocalLoading] = useState({})
  const [localError, setLocalError] = useState('')

  // 運行性能測試
  const handleRunPerformanceTest = useCallback(async (e) => {
    // 防止表單提交導致頁面跳轉
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }

    if (iterations < 1 || iterations > 1000) {
      setLocalError('Iterations must be between 1 and 1000!')
      return
    }

    try {
      setLocalLoading(prev => ({ ...prev, testing: true }))
      setLocalError('')
      clearError()
      
      const startTime = Date.now()
      const result = await apiService.performanceTest(iterations)
      const endTime = Date.now()
      const totalTime = endTime - startTime
      
      const testWithMetadata = {
        ...result,
        test_index: testResults.length,
        timestamp: new Date().toISOString(),
        total_test_time: totalTime,
        avg_per_iteration: totalTime / iterations
      }
      
      setTestResults(prev => [...prev, testWithMetadata])
      setSelectedResultIndex(testResults.length)
      
    } catch (err) {
      setLocalError('Performance test failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, testing: false }))
    }
  }, [iterations, testResults.length, clearError])

  // 清空測試結果
  const handleClearResults = useCallback((e) => {
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }
    setTestResults([])
    setSelectedResultIndex(-1)
    setLocalError('')
  }, [])

  // 選擇測試結果
  const handleSelectResult = useCallback((index) => {
    setSelectedResultIndex(index)
  }, [])

  // 設置迭代次數的處理函數
  const handleIterationChange = useCallback((e) => {
    const value = parseInt(e.target.value) || 100
    setIterations(Math.min(Math.max(value, 1), 1000))
  }, [])

  // 設置預設值的處理函數
  const handlePresetClick = useCallback((value, e) => {
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }
    setIterations(value)
  }, [])

  const getOutputContent = () => {
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (selectedResultIndex >= 0 && testResults[selectedResultIndex]) {
      const result = testResults[selectedResultIndex]
      const fastestOp = getFastestOperation(result)
      const slowestOp = getSlowestOperation(result)
      
      return `🏁 Performance Test Results - Test ${selectedResultIndex}
⏰ Test Time: ${result.timestamp}
🔄 Iterations: ${result.iterations}
⚡ Total Test Duration: ${result.total_test_time}ms
📊 Average per Iteration: ${result.avg_per_iteration.toFixed(2)}ms

📈 Detailed Performance Metrics (Average per Operation):

🏠 Address Generation: ${result.addr_gen_ms}ms
   ├─ Key pair to stealth address
   └─ Includes random element generation

🔍 Address Verification: ${result.addr_verify_ms}ms
   ├─ Full verification with pairing
   └─ Cryptographic proof validation

⚡ Fast Address Verification: ${result.fast_verify_ms}ms
   ├─ Optimized verification method
   └─ ~${((result.addr_verify_ms / result.fast_verify_ms) || 1).toFixed(1)}x faster than full verification

🔐 One-time Secret Key Generation: ${result.onetime_sk_ms}ms
   ├─ DSK derivation from address
   └─ Required for transaction operations

🔍 Identity Tracing: ${result.trace_ms}ms
   ├─ Recover identity from address
   └─ Trace authority operation

📊 Performance Analysis:
   Fastest Operation: ${fastestOp}
   Slowest Operation: ${slowestOp}
   Total Cycle Time: ${(result.addr_gen_ms + result.addr_verify_ms + result.fast_verify_ms + result.onetime_sk_ms + result.trace_ms).toFixed(3)}ms`
    }
    
    if (testResults.length > 0) {
      const latestResult = testResults[testResults.length - 1]
      const totalCoreTime = (latestResult.addr_gen_ms + latestResult.addr_verify_ms + 
                            latestResult.fast_verify_ms + latestResult.onetime_sk_ms + 
                            latestResult.trace_ms).toFixed(3)
      
      return `✅ SITAIBA Performance Test Completed!
🔄 Iterations: ${latestResult.iterations}
📊 Status: ${latestResult.status}

Key Metrics (Average per iteration):
• 🏠 Address Generation: ${latestResult.addr_gen_ms}ms
• 🔍 Address Verification: ${latestResult.addr_verify_ms}ms
• ⚡ Fast Address Verification: ${latestResult.fast_verify_ms}ms
• 🔑 One-time Secret Key Gen: ${latestResult.onetime_sk_ms}ms
• 🕵️ Identity Tracing: ${latestResult.trace_ms}ms

Total Core Operations Time: ${totalCoreTime}ms per iteration
${latestResult.note || 'All times exclude hash computation overhead'}`
    }
    
    return 'Configure test parameters and run performance analysis...'
  }

  // 輔助方法來找最快和最慢的操作
  const getFastestOperation = (result) => {
    const operations = {
      'Address Generation': result.addr_gen_ms,
      'Address Verification': result.addr_verify_ms,
      'Fast Verification': result.fast_verify_ms,
      'One-time SK': result.onetime_sk_ms,
      'Tracing': result.trace_ms
    }
    
    return Object.entries(operations).reduce((min, [name, time]) => 
      time < min.time ? { name, time } : min, 
      { name: 'Unknown', time: Infinity }
    ).name
  }

  const getSlowestOperation = (result) => {
    const operations = {
      'Address Generation': result.addr_gen_ms,
      'Address Verification': result.addr_verify_ms,
      'Fast Verification': result.fast_verify_ms,
      'One-time SK': result.onetime_sk_ms,
      'Tracing': result.trace_ms
    }
    
    return Object.entries(operations).reduce((max, [name, time]) => 
      time > max.time ? { name, time } : max, 
      { name: 'Unknown', time: -1 }
    ).name
  }

  const getIterationPresets = () => [
    { label: 'Quick Test (10)', value: 10 },
    { label: 'Standard (100)', value: 100 },
    { label: 'Intensive (500)', value: 500 },
    { label: 'Stress Test (1000)', value: 1000 }
  ]

  return (
    <Section title="📊 Performance Testing" className="performance-section">
      <div className="controls">
        <label>Number of Iterations:</label>
        <Input
          type="number"
          value={iterations}
          onChange={handleIterationChange}
          min="1"
          max="1000"
        />
        
        <div className="preset-buttons">
          <label>Quick Presets:</label>
          <div className="inline-controls">
            {getIterationPresets().map(preset => (
              <Button
                key={preset.value}
                onClick={(e) => handlePresetClick(preset.value, e)}
                variant="secondary"
                className="preset-btn"
                type="button"
              >
                {preset.label}
              </Button>
            ))}
          </div>
        </div>
        
        <div className="test-controls">
          <Button
            onClick={handleRunPerformanceTest}
            loading={localLoading.testing}
            disabled={localLoading.testing || iterations < 1 || iterations > 1000}
            className="test-button"
            type="button"
          >
            {localLoading.testing ? 'Running Test...' : 'Run Performance Test'}
          </Button>
          
          <Button
            onClick={handleClearResults}
            variant="secondary"
            disabled={testResults.length === 0}
            type="button"
          >
            Clear Results
          </Button>
        </div>
        
        {testResults.length > 0 && (
          <div className="results-selector">
            <label>View Test Results:</label>
            <select 
              value={selectedResultIndex} 
              onChange={(e) => handleSelectResult(parseInt(e.target.value))}
              className="select"
            >
              <option value={-1}>Select a test result...</option>
              {testResults.map((result, index) => (
                <option key={index} value={index}>
                  Test {index} - {result.iterations} iterations - {new Date(result.timestamp).toLocaleTimeString()}
                </option>
              ))}
            </select>
          </div>
        )}
        
        {localLoading.testing && (
          <div className="progress-indicator">
            <div className="progress-bar">
              <div className="progress-fill"></div>
            </div>
            <div className="progress-text">
              Running {iterations} iterations of cryptographic operations...
            </div>
          </div>
        )}
      </div>
      
      {testResults.length > 0 && (
        <div className="performance-display">
          {selectedResultIndex >= 0 && testResults[selectedResultIndex] && (
            <SitaibaPerformanceDisplay data={testResults[selectedResultIndex]} />
          )}
        </div>
      )}
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />
    </Section>
  )
}

export default PerformanceTest