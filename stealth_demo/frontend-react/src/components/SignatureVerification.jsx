import React, { useState, useCallback } from 'react'
import { Section, Button, Select, Input, Output } from './common'
import { apiService } from '../services/apiService'
import { useAppData } from '../hooks/useAppData'
import { truncateHex, isValidHex } from '../utils/helpers'

function SignatureVerification() {
  const { 
    addresses, 
    loading: globalLoading, 
    error: globalError, 
    clearError,
    loadAddresses
  } = useAppData()
  
  const [message, setMessage] = useState('')
  const [qSigmaHex, setQSigmaHex] = useState('')
  const [hHex, setHHex] = useState('')
  const [selectedAddrIndex, setSelectedAddrIndex] = useState('')
  const [verificationResult, setVerificationResult] = useState(null)
  const [localLoading, setLocalLoading] = useState({})
  const [localError, setLocalError] = useState('')

  // 刷新地址數據
  const handleRefreshAddresses = useCallback(async () => {
    setLocalError('')
    clearError()
    await loadAddresses()
  }, [loadAddresses, clearError])

  // 從測試簽名中導入數據（用於測試）
  const handleImportTestSignature = useCallback(() => {
    setMessage('Hello, this is a test message!')
    setQSigmaHex('1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef')
    setHHex('abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890')
    setSelectedAddrIndex('0')
  }, [])

  // 清空表單
  const handleClearForm = useCallback(() => {
    setMessage('')
    setQSigmaHex('')
    setHHex('')
    setSelectedAddrIndex('')
    setVerificationResult(null)
    setLocalError('')
  }, [])

  // 驗證簽名
  const handleVerifySignature = useCallback(async () => {
    // 驗證輸入
    if (!message.trim()) {
      setLocalError('Please enter the original message!')
      return
    }
    
    if (!qSigmaHex.trim()) {
      setLocalError('Please enter Q_sigma (signature component)!')
      return
    }
    
    if (!hHex.trim()) {
      setLocalError('Please enter H (hash component)!')
      return
    }
    
    if (selectedAddrIndex === '') {
      setLocalError('Please select an address!')
      return
    }
    
    // 驗證十六進制格式
    if (!isValidHex(qSigmaHex)) {
      setLocalError('Q_sigma must be a valid hexadecimal string!')
      return
    }
    
    if (!isValidHex(hHex)) {
      setLocalError('H must be a valid hexadecimal string!')
      return
    }

    try {
      setLocalLoading(prev => ({ ...prev, verifying: true }))
      setLocalError('')
      clearError()
      
      const result = await apiService.verifySignature(
        message,
        qSigmaHex,
        hHex,
        parseInt(selectedAddrIndex)
      )
      
      setVerificationResult({
        ...result,
        timestamp: new Date().toISOString(),
        input_message: message,
        input_q_sigma: qSigmaHex,
        input_h: hHex,
        used_address: addresses[parseInt(selectedAddrIndex)]
      })
      
    } catch (err) {
      setLocalError('Signature verification failed: ' + err.message)
      setVerificationResult(null)
    } finally {
      setLocalLoading(prev => ({ ...prev, verifying: false }))
    }
  }, [message, qSigmaHex, hHex, selectedAddrIndex, addresses, clearError])

  const getOutputContent = () => {
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (verificationResult) {
      const addr = verificationResult.used_address
      return `🔍 Signature Verification Results:
📝 Message: "${verificationResult.input_message}"
📧 Address: ${verificationResult.address_id}
✅ Verification Result: ${verificationResult.valid ? '✅ VALID' : '❌ INVALID'}
📊 Status: ${verificationResult.status}
⏰ Verified at: ${verificationResult.timestamp}

📋 Verification Details:
🏠 Used Address: ${addr?.id} - ${truncateHex(addr?.addr_hex)}
👤 Address Owner: ${addr?.key_id}

🔐 Input Signature Components:
Q_sigma: ${truncateHex(verificationResult.input_q_sigma, 20)}
H: ${truncateHex(verificationResult.input_h, 20)}

${verificationResult.valid ? 
  '🎉 Signature is mathematically valid!' : 
  '❌ Signature verification failed - either the signature is invalid or doesn\'t match the message/address.'
}`
    }
    
    return 'Enter message and signature components to verify...'
  }

  const isFormValid = message.trim() && qSigmaHex.trim() && hHex.trim() && selectedAddrIndex !== ''

  return (
    <Section title="🔍 Signature Verification">
      <div className="controls">
        <label>Original Message:</label>
        <Input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Enter the original message that was signed..."
        />
        
        <label>Q_sigma (Signature Component - G1 element in hex):</label>
        <Input
          value={qSigmaHex}
          onChange={(e) => setQSigmaHex(e.target.value)}
          placeholder="Enter Q_sigma as hexadecimal string..."
        />
        
        <label>H (Hash Component - Zr element in hex):</label>
        <Input
          value={hHex}
          onChange={(e) => setHHex(e.target.value)}
          placeholder="Enter H as hexadecimal string..."
        />
        
        <label>Select Address to Verify Against:</label>
        <Select
          value={selectedAddrIndex}
          onChange={(e) => setSelectedAddrIndex(e.target.value)}
        >
          <option value="">Select an address...</option>
          {addresses.map((addr, index) => (
            <option key={addr.id} value={index}>
              {addr.id} - Owner: {addr.key_id} - {truncateHex(addr.addr_hex, 8)}
            </option>
          ))}
        </Select>
        
        <div className="inline-controls">
          <Button
            onClick={handleRefreshAddresses}
            variant="secondary"
          >
            Refresh Addresses
          </Button>
          
          <Button
            onClick={handleImportTestSignature}
            variant="secondary"
          >
            Import Test Data
          </Button>
          
          <Button
            onClick={handleClearForm}
            variant="secondary"
          >
            Clear Form
          </Button>
          
          <Button
            onClick={handleVerifySignature}
            loading={localLoading.verifying}
            disabled={!isFormValid || localLoading.verifying}
          >
            Verify Signature
          </Button>
        </div>
        
        {verificationResult && (
          <div className={`verification-status ${verificationResult.valid ? 'valid' : 'invalid'}`}>
            <strong>
              {verificationResult.valid ? '✅ SIGNATURE VALID' : '❌ SIGNATURE INVALID'}
            </strong>
          </div>
        )}
      </div>
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />
      
      <style jsx>{`
        .verification-status {
          padding: 15px;
          border-radius: 8px;
          margin: 10px 0;
          text-align: center;
          font-size: 1.1em;
        }
        
        .verification-status.valid {
          background: #d4edda;
          border: 2px solid #28a745;
          color: #155724;
        }
        
        .verification-status.invalid {
          background: #f8d7da;
          border: 2px solid #dc3545;
          color: #721c24;
        }
      `}</style>
    </Section>
  )
}

export default SignatureVerification