import React, { useState, useCallback } from 'react'
import { Section, Button, Input, Output } from '../../components/common'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'

function StealthPerformanceTest() {
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

  const handleRunPerformanceTest = useCallback(async (e) => {
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }

    if (iterations < 1 || iterations > 1000) {
      setLocalError('Iteration count must be between 1 and 1000!')
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
      setLocalError('Stealth performance test failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, testing: false }))
    }
  }, [iterations, testResults.length, clearError])

  const handleClearResults = useCallback((e) => {
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }
    setTestResults([])
    setSelectedResultIndex(-1)
    setLocalError('')
  }, [])

  const handleSelectResult = useCallback((index) => {
    setSelectedResultIndex(index)
  }, [])

  const handleIterationChange = useCallback((e) => {
    const value = parseInt(e.target.value) || 100
    setIterations(Math.min(Math.max(value, 1), 1000))
  }, [])

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
      
      return `🏁 Stealth Scheme Performance Test Results - Test ${selectedResultIndex}
⏰ Test Time: ${result.timestamp}
🔄 Iterations: ${result.iterations}
⚡ Total Test Duration: ${result.total_test_time}ms
📊 Average per Iteration: ${result.avg_per_iteration.toFixed(2)}ms
🎯 Scheme: Stealth

📈 Detailed Performance Metrics (Average time per operation):

🏠 Address Generation: ${result.addr_gen_ms}ms
   ├─ Key pair to stealth address
   └─ Includes random element generation

🔍 Address Recognition: ${result.addr_recognize_ms}ms
   ├─ Full recognition pairing computation
   └─ Cryptographic proof verification

⚡ Fast Address Recognition: ${result.fast_recognize_ms}ms
   ├─ Optimized recognition method
   └─ ~${((result.addr_recognize_ms / result.fast_recognize_ms) || 1).toFixed(1)}x faster than full recognition

🔐 One-time Secret Key Generation: ${result.onetime_sk_ms}ms
   ├─ Derive DSK from address
   └─ Required for signing operations

✍️ Message Signing: ${result.sign_ms}ms
   ├─ Cryptographic signature generation
   └─ Includes random nonce generation

✅ Signature Verification: ${result.sig_verify_ms}ms
   ├─ Pairing verification
   └─ Mathematical proof verification

🔍 Identity Tracing: ${result.trace_ms}ms
   ├─ Recover identity from address
   └─ Tracing authority operation

📊 Performance Analysis:
   Fastest Operation: ${fastestOp}
   Slowest Operation: ${slowestOp}
   Total Cycle Time: ${(result.addr_gen_ms + result.fast_recognize_ms + result.onetime_sk_ms + result.sign_ms + result.sig_verify_ms + result.trace_ms).toFixed(3)}ms`
    }
    
    if (testResults.length > 0) {
      const latestResult = testResults[testResults.length - 1]
      return `✅ Stealth Performance Test Completed!
🔄 Iterations: ${latestResult.iterations}
⚡ Total Time: ${latestResult.total_test_time}ms
📊 Average/Iteration: ${latestResult.avg_per_iteration.toFixed(2)}ms

Key Metrics:
• Address Generation: ${latestResult.addr_gen_ms}ms
• Fast Recognition: ${latestResult.fast_recognize_ms}ms  
• Signing: ${latestResult.sign_ms}ms
• Verification: ${latestResult.sig_verify_ms}ms
• Tracing: ${latestResult.trace_ms}ms`
    }
    
    return 'Configure test parameters and run Stealth scheme performance analysis...'
  }

  const getFastestOperation = (result) => {
    const operations = {
      'Address Generation': result.addr_gen_ms,
      'Fast Recognition': result.fast_recognize_ms,
      'DSK Generation': result.onetime_sk_ms,
      'Signing': result.sign_ms,
      'Signature Verification': result.sig_verify_ms,
      'Identity Tracing': result.trace_ms
    }
    
    return Object.entries(operations).reduce((min, [name, time]) => 
      time < min.time ? { name, time } : min, 
      { name: 'Unknown', time: Infinity }
    ).name
  }

  const getSlowestOperation = (result) => {
    const operations = {
      'Address Generation': result.addr_gen_ms,
      'Full Recognition': result.addr_recognize_ms,
      'Fast Recognition': result.fast_recognize_ms,
      'DSK Generation': result.onetime_sk_ms,
      'Signing': result.sign_ms,
      'Signature Verification': result.sig_verify_ms,
      'Identity Tracing': result.trace_ms
    }
    
    return Object.entries(operations).reduce((max, [name, time]) => 
      time > max.time ? { name, time } : max, 
      { name: 'Unknown', time: -1 }
    ).name
  }

  const getIterationPresets = () => [
    { label: 'Quick Test (10)', value: 10 },
    { label: 'Standard Test (100)', value: 100 },
    { label: 'Intensive Test (500)', value: 500 },
    { label: 'Stress Test (1000)', value: 1000 }
  ]

  return (
    <Section title="📊 Performance Test (Stealth)" className="performance-section">
      <div className="controls">
        <label>Iterations:</label>
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
            {localLoading.testing ? 'Running Test...' : 'Run Stealth Performance Test'}
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
              <option value={-1}>Select test result...</option>
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
              Running {iterations} Stealth cryptographic operation iterations...
            </div>
          </div>
        )}
      </div>
      
      {testResults.length > 0 && (
        <div className="performance-grid">
          {selectedResultIndex >= 0 && testResults[selectedResultIndex] && (
            <>
              <div className="perf-metric">
                <div className="perf-value">{testResults[selectedResultIndex].addr_gen_ms}ms</div>
                <div className="perf-label">Address Generation</div>
              </div>
              <div className="perf-metric">
                <div className="perf-value">{testResults[selectedResultIndex].fast_recognize_ms}ms</div>
                <div className="perf-label">Fast Recognition</div>
              </div>
              <div className="perf-metric">
                <div className="perf-value">{testResults[selectedResultIndex].sign_ms}ms</div>
                <div className="perf-label">Signing</div>
              </div>
              <div className="perf-metric">
                <div className="perf-value">{testResults[selectedResultIndex].sig_verify_ms}ms</div>
                <div className="perf-label">Signature Verification</div>
              </div>
              <div className="perf-metric">
                <div className="perf-value">{testResults[selectedResultIndex].trace_ms}ms</div>
                <div className="perf-label">Identity Tracing</div>
              </div>
              <div className="perf-metric">
                <div className="perf-value">{testResults[selectedResultIndex].total_test_time}ms</div>
                <div className="perf-label">Total Time</div>
              </div>
            </>
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

export default StealthPerformanceTest