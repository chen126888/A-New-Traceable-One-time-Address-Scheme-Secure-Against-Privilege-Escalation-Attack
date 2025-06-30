import React, { useState, useCallback } from 'react'
import { Section, Button, Input, Output } from './common'
import { apiService } from '../services/apiService'
import { useAppData } from '../hooks/useAppData'

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
  const handleRunPerformanceTest = useCallback(async () => {
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
  const handleClearResults = useCallback(() => {
    setTestResults([])
    setSelectedResultIndex(-1)
    setLocalError('')
  }, [])

  // 選擇測試結果
  const handleSelectResult = useCallback((index) => {
    setSelectedResultIndex(index)
  }, [])

  const getOutputContent = () => {
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (selectedResultIndex >= 0 && testResults[selectedResultIndex]) {
      const result = testResults[selectedResultIndex]
      
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
   └─ Required for signing operations

✍️ Message Signing: ${result.sign_ms}ms
   ├─ Cryptographic signature generation
   └─ Includes random nonce generation

✅ Signature Verification: ${result.sig_verify_ms}ms
   ├─ Pairing-based verification
   └─ Mathematical proof validation

🔍 Identity Tracing: ${result.trace_ms}ms
   ├─ Recover identity from address
   └─ Trace authority operation

📊 Performance Analysis:
   Fastest Operation: ${this.getFastestOperation(result)}
   Slowest Operation: ${this.getSlowestOperation(result)}
   Total Cycle Time: ${(result.addr_gen_ms + result.fast_verify_ms + result.onetime_sk_ms + result.sign_ms + result.sig_verify_ms + result.trace_ms).toFixed(3)}ms`
    }
    
    if (testResults.length > 0) {
      const latestResult = testResults[testResults.length - 1]
      return `✅ Performance Test Completed!
🔄 Iterations: ${latestResult.iterations}
⚡ Total Time: ${latestResult.total_test_time}ms
📊 Avg/Iteration: ${latestResult.avg_per_iteration.toFixed(2)}ms

Key Metrics:
• Address Gen: ${latestResult.addr_gen_ms}ms
• Fast Verify: ${latestResult.fast_verify_ms}ms  
• Signing: ${latestResult.sign_ms}ms
• Verification: ${latestResult.sig_verify_ms}ms
• Tracing: ${latestResult.trace_ms}ms`
    }
    
    return 'Configure test parameters and run performance analysis...'
  }

  // 輔助方法來找最快和最慢的操作
  const getFastestOperation = (result) => {
    const operations = {
      'Address Generation': result.addr_gen_ms,
      'Fast Verification': result.fast_verify_ms,
      'One-time SK': result.onetime_sk_ms,
      'Signing': result.sign_ms,
      'Sig Verification': result.sig_verify_ms,
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
      'Full Verification': result.addr_verify_ms,
      'Fast Verification': result.fast_verify_ms,
      'One-time SK': result.onetime_sk_ms,
      'Signing': result.sign_ms,
      'Sig Verification': result.sig_verify_ms,
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
          onChange={(e) => setIterations(parseInt(e.target.value) || 100)}
          min="1"
          max="1000"
        />
        
        <div className="preset-buttons">
          <label>Quick Presets:</label>
          <div className="inline-controls">
            {getIterationPresets().map(preset => (
              <Button
                key={preset.value}
                onClick={() => setIterations(preset.value)}
                variant="secondary"
                className="preset-btn"
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
          >
            {localLoading.testing ? 'Running Test...' : 'Run Performance Test'}
          </Button>
          
          <Button
            onClick={handleClearResults}
            variant="secondary"
            disabled={testResults.length === 0}
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
        <div className="performance-grid">
          {selectedResultIndex >= 0 && testResults[selectedResultIndex] && (
            <>
              <div className="perf-metric">
                <div className="perf-value">{testResults[selectedResultIndex].addr_gen_ms}ms</div>
                <div className="perf-label">Address Gen</div>
              </div>
              <div className="perf-metric">
                <div className="perf-value">{testResults[selectedResultIndex].fast_verify_ms}ms</div>
                <div className="perf-label">Fast Verify</div>
              </div>
              <div className="perf-metric">
                <div className="perf-value">{testResults[selectedResultIndex].sign_ms}ms</div>
                <div className="perf-label">Signing</div>
              </div>
              <div className="perf-metric">
                <div className="perf-value">{testResults[selectedResultIndex].sig_verify_ms}ms</div>
                <div className="perf-label">Sig Verify</div>
              </div>
              <div className="perf-metric">
                <div className="perf-value">{testResults[selectedResultIndex].trace_ms}ms</div>
                <div className="perf-label">Tracing</div>
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
      
      <style jsx>{`
        .preset-buttons {
          margin: 10px 0;
        }
        
        .preset-btn {
          margin: 2px;
          padding: 8px 12px;
          font-size: 0.85em;
        }
        
        .test-controls {
          margin: 15px 0;
        }
        
        .test-button {
          min-width: 180px;
          margin-right: 10px;
        }
        
        .results-selector {
          margin: 15px 0;
        }
        
        .progress-indicator {
          margin: 15px 0;
          text-align: center;
        }
        
        .progress-bar {
          width: 100%;
          height: 6px;
          background: #f0f0f0;
          border-radius: 3px;
          overflow: hidden;
          margin: 10px 0;
        }
        
        .progress-fill {
          height: 100%;
          background: linear-gradient(45deg, #667eea, #764ba2);
          animation: progress 3s ease-in-out infinite;
        }
        
        .progress-text {
          color: #666;
          font-size: 0.9em;
        }
        
        @keyframes progress {
          0% { width: 0%; }
          50% { width: 70%; }
          100% { width: 100%; }
        }
      `}</style>
    </Section>
  )
}

export default PerformanceTest