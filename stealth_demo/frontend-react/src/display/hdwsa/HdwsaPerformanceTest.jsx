import React, { useState } from 'react'
import { Section, Button, Input, Output } from '../../components/common'
import { apiService } from '../../services/apiService'

function HdwsaPerformanceTest() {
  const [iterations, setIterations] = useState(10)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [results, setResults] = useState(null)

  const handleRunTest = async () => {
    if (iterations < 1 || iterations > 1000) {
      setError('Please enter a number between 1 and 1000')
      return
    }

    try {
      setLoading(true)
      setError('')
      setResults(null)
      
      const testResults = await apiService.performanceTest(iterations)
      setResults(testResults)
      
    } catch (err) {
      setError('Performance test failed: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const getOutputContent = () => {
    if (error) {
      return `Error: ${error}`
    }
    
    if (results) {
      return `🏃 HDWSA Performance Test Results:
📊 Test Configuration:
  • Total Iterations: ${results.iterations || iterations}
  • Successful Operations: ${results.successful_operations || 0}
  • Success Rate: ${(results.success_rate || 0).toFixed(2)}%

⏱️ Average Performance Times:
  • Root Key Generation: ${(results.root_keygen_avg || 0).toFixed(3)} ms
  • User Key Generation: ${(results.keypair_gen_avg || 0).toFixed(3)} ms  
  • Address Generation: ${(results.addr_gen_avg || 0).toFixed(3)} ms
  • Address Recognition: ${(results.addr_recognize_avg || 0).toFixed(3)} ms
  • DSK Generation: ${(results.dsk_gen_avg || 0).toFixed(3)} ms
  • Message Signing: ${(results.sign_avg || 0).toFixed(3)} ms
  • Signature Verification: ${(results.verify_avg || 0).toFixed(3)} ms

🔧 Hash Function Performance:
  • H0 (ID→G1): ${(results.h0_avg || 0).toFixed(3)} ms
  • H1 (G1×G1→Zr): ${(results.h1_avg || 0).toFixed(3)} ms  
  • H2 (G1×G1→Zr): ${(results.h2_avg || 0).toFixed(3)} ms
  • H3 (G1×G1×G1→G1): ${(results.h3_avg || 0).toFixed(3)} ms
  • H4 (Signature Hash): ${(results.h4_avg || 0).toFixed(3)} ms

📈 Performance Summary:
  • Total Operations: ${results.operation_count || 0}
  • Overall Status: ${results.successful_operations === results.iterations ? '✅ All tests passed' : '⚠️ Some tests failed'}
  
💡 HDWSA Performance Characteristics:
  • Hierarchical key derivation enables scalable wallet management
  • Pairing-based operations provide strong security guarantees
  • Address recognition uses unified algorithm for efficiency
  • DSK generation enables secure message signing`
    }
    
    return `Run a performance test to measure HDWSA cryptographic operations.
    
This test will:
🔑 Generate hierarchical wallet keys
🏠 Create addresses from wallets  
🔐 Generate DSKs for signing
✍️ Sign and verify test messages
📊 Measure average execution times`
  }

  return (
    <Section title="🏃 HDWSA Performance Test">
      <div className="controls">
        <div className="input-group">
          <Input
            label="Number of Iterations:"
            type="number"
            value={iterations}
            onChange={(e) => setIterations(parseInt(e.target.value) || 1)}
            min="1"
            max="1000"
            disabled={loading}
          />
          
          <div className="iteration-info">
            <p>ℹ️ Each iteration performs a complete HDWSA workflow:</p>
            <ul>
              <li>Generate hierarchical wallet keys</li>
              <li>Create address from wallet</li> 
              <li>Generate DSK for the address</li>
              <li>Sign a test message</li>
              <li>Verify the signature</li>
            </ul>
            <p><strong>Recommended:</strong> Start with 10-50 iterations for quick tests.</p>
          </div>
        </div>

        <div className="button-group">
          <Button
            onClick={handleRunTest}
            loading={loading}
            disabled={loading || iterations < 1 || iterations > 1000}
            variant="primary"
          >
            {loading ? '🔄 Running Test...' : '🏃 Run Performance Test'}
          </Button>
        </div>
      </div>
      
      <Output 
        content={getOutputContent()}
        isError={!!error}
      />

      <div className="hdwsa-info">
        <h4>ℹ️ HDWSA Performance Testing Information</h4>
        <div className="info-content">
          <p><strong>🏃 Purpose:</strong> Measure the performance of HDWSA cryptographic operations</p>
          <p><strong>📊 Metrics:</strong> Average execution times for key operations and hash functions</p>
          <p><strong>🏗️ Hierarchical:</strong> Tests complete workflow including wallet derivation</p>
          <p><strong>🔒 Security:</strong> Performance measured while maintaining cryptographic security</p>
          <p><strong>⚡ Optimization:</strong> Results help identify performance bottlenecks</p>
        </div>
      </div>

      <style jsx>{`
        .controls {
          display: flex;
          flex-direction: column;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .input-group {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .button-group {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .iteration-info {
          background: #e7f3ff;
          border: 1px solid #b3d9ff;
          border-radius: 4px;
          padding: 1rem;
          font-size: 13px;
          color: #495057;
        }

        .iteration-info p {
          margin: 0 0 0.5rem 0;
        }

        .iteration-info ul {
          margin: 0.5rem 0;
          padding-left: 1.5rem;
        }

        .iteration-info li {
          margin: 0.25rem 0;
        }

        .iteration-info strong {
          color: #0056b3;
        }

        .hdwsa-info {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 4px;
          padding: 1rem;
          margin-top: 1rem;
        }

        .hdwsa-info h4 {
          margin: 0 0 0.75rem 0;
          color: #495057;
          font-size: 14px;
        }

        .info-content p {
          margin: 0.5rem 0;
          font-size: 13px;
          line-height: 1.4;
          color: #6c757d;
        }

        .info-content strong {
          color: #495057;
        }
      `}</style>
    </Section>
  )
}

export default HdwsaPerformanceTest