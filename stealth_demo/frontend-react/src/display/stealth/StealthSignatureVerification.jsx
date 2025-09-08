import React, { useState, useCallback, useEffect } from 'react'
import { Section, Button, Select, Input, Output } from '../../components/common'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'
import { truncateHex, isValidHex } from '../../utils/helpers'

function StealthSignatureVerification() {
  const { 
    addresses,
    txMessages,
    loading: globalLoading, 
    error: globalError, 
    clearError,
    loadAddresses,
    loadTxMessages
  } = useAppData()
  
  const [selectedTxIndex, setSelectedTxIndex] = useState('')
  const [useManualInput, setUseManualInput] = useState(false)
  const [manualTxData, setManualTxData] = useState({
    message: '',
    qSigmaHex: '',
    hHex: '',
    addrHex: '',
    r2Hex: '',
    cHex: ''
  })
  const [verificationResult, setVerificationResult] = useState(null)
  const [localLoading, setLocalLoading] = useState({})
  const [localError, setLocalError] = useState('')


  // 監聽簽名事件來創建完整的交易訊息
  useEffect(() => {
    const handleSignatureCreated = (event) => {
      console.log('Signature Verification received signature:', event.detail)
      const { signature } = event.detail
      
      // 找到對應的地址數據
      let addressData = null
      if (signature.address_index !== undefined) {
        addressData = addresses[signature.address_index]
      } else if (signature.address_id) {
        addressData = addresses.find(addr => addr.id === signature.address_id)
      }
      
      console.log('Found address data:', addressData)
      
      if (addressData) {
        // 創建完整的交易訊息 tx = (addr, R, m, σ)
        const txMessage = {
          id: `tx_${Date.now()}`,
          index: txMessages.length,
          timestamp: new Date().toISOString(),
          
          // 交易組件
          message: signature.message,                    // m: 原始訊息
          signature: {
            q_sigma_hex: signature.q_sigma_hex,         // σ.Q_σ: 簽名組件1
            h_hex: signature.h_hex                      // σ.H: 簽名組件2
          },
          address: {
            addr_hex: addressData.addr_hex,             // addr: 簽名地址
            r2_hex: addressData.r2_hex,                 // R.r2: 地址組件
            c_hex: addressData.c_hex,                   // R.c: 地址組件
            owner_id: addressData.key_id                // 地址擁有者ID
          },
          
          // 元數據
          signing_method: signature.method,
          status: 'pending_verification'
        }
        
        console.log('Creating transaction message:', txMessage)
        // Note: Transaction message is already added to global state by MessageSigning component
      } else {
        console.warn('No address data found for signature:', signature)
      }
    }

    // 載入交易訊息（現在有防護機制，不會覆蓋前端狀態）
    loadTxMessages()
    
    // 監聽新事件
    window.addEventListener('signatureCreated', handleSignatureCreated)

    return () => {
      window.removeEventListener('signatureCreated', handleSignatureCreated)
    }
  }, [loadTxMessages, addresses])

  // 刷新數據
  const handleRefreshData = useCallback(async () => {
    setLocalError('')
    clearError()
    await Promise.all([
      loadAddresses(),
      loadTxMessages() // 這現在有防護機制，不會覆蓋現有的前端資料
    ])
    console.log('Refreshed data, txMessages count:', txMessages.length)
  }, [loadAddresses, loadTxMessages, clearError, txMessages.length])



  // 驗證交易
  const handleVerifyTransaction = useCallback(async () => {
    console.log('Verify transaction clicked!')
    
    let txData = null
    
    if (useManualInput) {
      // 使用手動輸入的數據
      if (!manualTxData.message.trim() || !manualTxData.qSigmaHex.trim() || 
          !manualTxData.hHex.trim() || !manualTxData.addrHex.trim() ||
          !manualTxData.r2Hex.trim() || !manualTxData.cHex.trim()) {
        setLocalError('Please fill in all transaction components!')
        return
      }
      
      // 驗證十六進制格式
      const hexFields = ['qSigmaHex', 'hHex', 'addrHex', 'r2Hex', 'cHex']
      for (const field of hexFields) {
        if (!isValidHex(manualTxData[field])) {
          setLocalError(`${field} must be a valid hexadecimal string!`)
          return
        }
      }
      
      txData = {
        message: manualTxData.message,
        signature: {
          q_sigma_hex: manualTxData.qSigmaHex,
          h_hex: manualTxData.hHex
        },
        address: {
          addr_hex: manualTxData.addrHex,
          r2_hex: manualTxData.r2Hex,
          c_hex: manualTxData.cHex
        }
      }
    } else {
      // 使用選定的交易
      if (selectedTxIndex === '') {
        setLocalError('Please select a transaction to verify!')
        return
      }
      
      txData = txMessages[parseInt(selectedTxIndex)]
      if (!txData) {
        setLocalError('Invalid transaction selection!')
        return
      }
    }

    console.log('Transaction data to verify:', txData)

    try {
      setLocalLoading(prev => ({ ...prev, verifying: true }))
      setLocalError('')
      clearError()
      
      // 嘗試使用新的交易驗證API
      let result
      try {
        console.log('Trying new transaction verification API...')
        result = await apiService.post('/verify_transaction', {
          message: txData.message,
          q_sigma_hex: txData.signature.q_sigma_hex,
          h_hex: txData.signature.h_hex,
          addr_hex: txData.address.addr_hex,
          r2_hex: txData.address.r2_hex,
          c_hex: txData.address.c_hex
        })
        console.log('New API result:', result)
      } catch (newApiError) {
        console.log('New API failed, trying fallback:', newApiError.message)
        
        // 檢查是否有必要的數據進行回退
        if (!txData.address?.addr_hex) {
          throw new Error('Missing address data for verification')
        }
        
        if (!addresses || addresses.length === 0) {
          throw new Error('No addresses loaded for fallback verification')
        }
        
        // 後退方案：找到對應的地址索引並使用舊API
        const addressIndex = addresses.findIndex(addr => 
          addr && addr.addr_hex && addr.addr_hex === txData.address.addr_hex
        )
        
        if (addressIndex >= 0) {
          console.log('Using fallback API with address index:', addressIndex)
          result = await apiService.verifySignature(
            txData.message,
            txData.signature.q_sigma_hex,
            txData.signature.h_hex,
            addressIndex
          )
          console.log('Fallback API result:', result)
          result.fallback_method = true
        } else {
          throw new Error(`Cannot find matching address for verification. Looking for: ${txData.address.addr_hex}, Available addresses: ${addresses.filter(addr => addr && addr.addr_hex).map(addr => addr.addr_hex).join(', ')}`)
        }
      }
      
      setVerificationResult({
        ...result,
        timestamp: new Date().toISOString(),
        transaction_data: txData,
        verification_type: useManualInput ? 'manual' : 'auto'
      })
      
      // 更新交易狀態 - Note: This would need to be handled by a global state update function
      // For now, we'll just log it since txMessages is read-only from global state
      if (!useManualInput && selectedTxIndex !== '') {
        console.log(`Transaction ${selectedTxIndex} verification result: ${result.valid ? 'verified' : 'invalid'}`)
        // TODO: Implement global state update for transaction status
      }
      
      console.log('Verification completed:', result)
      
    } catch (err) {
      console.error('Verification failed:', err)
      setLocalError('Transaction verification failed: ' + err.message)
      setVerificationResult(null)
    } finally {
      setLocalLoading(prev => ({ ...prev, verifying: false }))
    }
  }, [useManualInput, manualTxData, selectedTxIndex, txMessages, addresses, clearError])

  const getOutputContent = () => {
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (verificationResult) {
      const txData = verificationResult.transaction_data
      return `🔍 Transaction Verification Results:
📝 Message: "${txData.message}"
📧 Address: ${truncateHex(txData.address.addr_hex)}
✅ Verification Result: ${verificationResult.valid ? '✅ VALID' : '❌ INVALID'}
📊 Status: ${verificationResult.status}
⏰ Verified at: ${verificationResult.timestamp}
🛠️ Method: ${verificationResult.verification_type}${verificationResult.fallback_method ? ' (fallback)' : ''}

📋 Transaction Components (addr, R, m, σ):
🏠 Address (addr): ${truncateHex(txData.address.addr_hex, 20)}
🎲 R2: ${truncateHex(txData.address.r2_hex, 20)}
🔒 C: ${truncateHex(txData.address.c_hex, 20)}
📝 Message (m): "${txData.message}"
✍️ Q_sigma (σ.Q): ${truncateHex(txData.signature.q_sigma_hex, 20)}
🔢 H (σ.H): ${truncateHex(txData.signature.h_hex, 20)}

${txData.address.owner_id ? `👤 Address Owner: ${txData.address.owner_id}` : ''}

${verificationResult.valid ? 
  '🎉 Transaction signature is mathematically valid!' : 
  '❌ Transaction verification failed - the signature does not match the transaction data.'
}`
    }
    
    if (txMessages.length === 0) {
      return 'Create signatures in the "Message Signing" section to verify complete transactions here.'
    }
    
    return 'Select a transaction to verify or use manual input mode...'
  }

  return (
    <Section title="🔍 Signature Verification (Stealth)">
      <div className="controls">
        <label>Verification Mode:</label>
        <Select
          value={useManualInput ? 'manual' : 'auto'}
          onChange={(e) => setUseManualInput(e.target.value === 'manual')}
        >
          <option value="auto">Transaction List (tx = addr, R, m, σ)</option>
          <option value="manual">Manual Transaction Input</option>
        </Select>
        
        {!useManualInput ? (
          <>
            <label>Select Transaction to Verify:</label>
            <Select
              value={selectedTxIndex}
              onChange={(e) => setSelectedTxIndex(e.target.value)}
            >
              <option value="">
                {txMessages.length === 0 
                  ? 'No transactions available - Sign a message first'
                  : 'Select a transaction to verify...'
                }
              </option>
              {txMessages.map((tx, index) => (
                <option key={tx.id || index} value={index}>
                  Tx {index}: "{tx.message?.substring(0, 25)}{tx.message?.length > 25 ? '...' : ''}" 
                  - {tx.signing_method} - {tx.status}
                </option>
              ))}
            </Select>
            
            {selectedTxIndex !== '' && txMessages[parseInt(selectedTxIndex)] && (
              <div className="tx-preview">
                <strong>📋 Transaction Preview:</strong>
                <div>🏠 Address: {truncateHex(txMessages[parseInt(selectedTxIndex)].address?.addr_hex, 16)}</div>
                <div>📝 Message: "{txMessages[parseInt(selectedTxIndex)].message}"</div>
                <div>✍️ Signature: {truncateHex(txMessages[parseInt(selectedTxIndex)].signature?.q_sigma_hex, 16)}</div>
                <div>📊 Status: {txMessages[parseInt(selectedTxIndex)].status}</div>
              </div>
            )}
          </>
        ) : (
          <div className="manual-input">
            <label>📝 Message (m):</label>
            <Input
              value={manualTxData.message}
              onChange={(e) => setManualTxData(prev => ({ ...prev, message: e.target.value }))}
              placeholder="Enter the original message..."
            />
            
            <label>🏠 Address (addr) - hex:</label>
            <Input
              value={manualTxData.addrHex}
              onChange={(e) => setManualTxData(prev => ({ ...prev, addrHex: e.target.value }))}
              placeholder="Enter address as hexadecimal..."
            />
            
            <label>🎲 R2 Component - hex:</label>
            <Input
              value={manualTxData.r2Hex}
              onChange={(e) => setManualTxData(prev => ({ ...prev, r2Hex: e.target.value }))}
              placeholder="Enter R2 as hexadecimal..."
            />
            
            <label>🔒 C Component - hex:</label>
            <Input
              value={manualTxData.cHex}
              onChange={(e) => setManualTxData(prev => ({ ...prev, cHex: e.target.value }))}
              placeholder="Enter C as hexadecimal..."
            />
            
            <label>✍️ Q_sigma (σ.Q) - hex:</label>
            <Input
              value={manualTxData.qSigmaHex}
              onChange={(e) => setManualTxData(prev => ({ ...prev, qSigmaHex: e.target.value }))}
              placeholder="Enter Q_sigma as hexadecimal..."
            />
            
            <label>🔢 H (σ.H) - hex:</label>
            <Input
              value={manualTxData.hHex}
              onChange={(e) => setManualTxData(prev => ({ ...prev, hHex: e.target.value }))}
              placeholder="Enter H as hexadecimal..."
            />
          </div>
        )}
        
        <div className="inline-controls">
          <Button
            onClick={handleVerifyTransaction}
            loading={localLoading.verifying}
            disabled={localLoading.verifying || 
              (!useManualInput && selectedTxIndex === '') ||
              (useManualInput && (!manualTxData.message.trim() || !manualTxData.qSigmaHex.trim()))
            }
          >
            Verify Transaction
          </Button>
          
          <Button
            onClick={handleRefreshData}
            variant="secondary"
          >
            Refresh Data
          </Button>
        </div>
        
        {verificationResult && (
          <div className={`verification-status ${verificationResult.valid ? 'valid' : 'invalid'}`}>
            <strong>
              {verificationResult.valid ? '✅ TRANSACTION VALID' : '❌ TRANSACTION INVALID'}
            </strong>
          </div>
        )}
      </div>
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />
    </Section>
  )
}

export default StealthSignatureVerification