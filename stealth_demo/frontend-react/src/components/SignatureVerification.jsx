import React, { useState, useCallback, useEffect } from 'react'
import { Section, Button, Select, Input, Output } from './common'
import { apiService } from '../services/apiService'
import { useAppData } from '../hooks/useAppData'
import { truncateHex, isValidHex } from '../utils/helpers'
import { getDisplayComponent } from './displays'

function SignatureVerification({ activeScheme }) {
  const { 
    transactions,  // 使用 global transactions 列表
    addresses,     // 需要 addresses 用於 fallback API
    loading: globalLoading, 
    error: globalError, 
    clearError
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

  // 簡化的刷新數據函數
  const handleRefreshData = useCallback(() => {
    setLocalError('')
    clearError()
    // transactions 會自動從 global state 更新，不需要手動載入
  }, [clearError])



  // 清空選擇
  const handleClearSelection = useCallback(() => {
    setSelectedTxIndex('')
    setVerificationResult(null)
    setLocalError('')
    setManualTxData({
      message: '',
      qSigmaHex: '',
      hHex: '',
      addrHex: '',
      r2Hex: '',
      cHex: ''
    })
  }, [])

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
      
      txData = transactions[parseInt(selectedTxIndex)]
      if (!txData) {
        setLocalError('Invalid transaction selection!')
        return
      }
    }

    console.log('Transaction data to verify:', txData)
    
    // 檢查交易數據是否完整
    if (txData.status === 'incomplete_address_data' || 
        txData.address.addr_hex === 'unknown' ||
        txData.address.r2_hex === 'unknown' ||
        txData.address.c_hex === 'unknown') {
      setLocalError('Cannot verify transaction: Address data is incomplete. Please refresh data and try again.')
      return
    }

    try {
      setLocalLoading(prev => ({ ...prev, verifying: true }))
      setLocalError('')
      clearError()
      
      // 直接使用交易中的資料進行驗證，不需要查找地址索引
      console.log('Using verifySignatureWithTxData API with transaction data')
      console.log('Transaction address data:', txData.address)
      console.log('Verification parameters:', {
        message: txData.message,
        q_sigma_hex: txData.signature.q_sigma_hex,
        h_hex: txData.signature.h_hex,
        addr_hex: txData.address.addr_hex,
        r2_hex: txData.address.r2_hex,
        c_hex: txData.address.c_hex
      })
      console.log('Signature data:', txData.signature)
      
      const result = await apiService.verifySignatureWithTxData({
        message: txData.message,
        q_sigma_hex: txData.signature.q_sigma_hex,
        h_hex: txData.signature.h_hex,
        addr_hex: txData.address.addr_hex,
        r2_hex: txData.address.r2_hex,
        c_hex: txData.address.c_hex
      })
      console.log('Verify signature API raw result:', result)
      console.log('Result properties:', Object.keys(result))
      console.log('Result.valid:', result.valid)
      console.log('Result.is_valid:', result.is_valid)
      console.log('Result.status:', result.status)
      
      // 標準化結果，確保有 valid 字段
      const normalizedResult = {
        ...result,
        valid: result.valid ?? result.is_valid,  // 處理不同 API 返回格式
        timestamp: new Date().toISOString(),
        transaction_data: txData,
        verification_type: useManualInput ? 'manual' : 'auto'
      }
      
      console.log('Normalized verification result:', normalizedResult)
      setVerificationResult(normalizedResult)
      
      // 注意：在這個新架構中，我們不再更新本地狀態
      // 如果需要更新交易狀態，應該通過 global state management 來處理
      
      console.log('Verification completed:', result)
      
    } catch (err) {
      console.error('Verification failed:', err)
      setLocalError('Transaction verification failed: ' + err.message)
      setVerificationResult(null)
    } finally {
      setLocalLoading(prev => ({ ...prev, verifying: false }))
    }
  }, [useManualInput, manualTxData, selectedTxIndex, transactions, clearError])

  const getOutputContent = () => {
    // 使用 scheme-specific 的 Display 組件
    const SignatureVerificationDisplay = getDisplayComponent(activeScheme, 'SignatureVerificationDisplay')
    if (SignatureVerificationDisplay) {
      return SignatureVerificationDisplay({
        verificationResult,
        transactions,
        selectedTxIndex,
        localError,
        globalError
      })
    }
    
    // fallback to default sitaiba display
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
🛠️ Method: ${verificationResult.verification_type}

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
    
    if (transactions.length === 0) {
      return `📋 About Transaction Verification:
This verifies complete transaction messages in the format:
tx = (addr, R, m, σ) where:
• addr: The signing address
• R: Address components (R2, C)  
• m: The original message
• σ: Signature components (Q_σ, H)

🔄 Getting Started:
1. Create signatures in the "Message Signing" section
2. Return here to verify complete transactions
3. All transaction components are automatically included

💡 No manual address selection needed - the address is part of the transaction!`
    }
    
    return 'Select a transaction to verify or use manual input mode...'
  }

  return (
    <Section title="🔍 Signature Verification">
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
                {transactions.length === 0 
                  ? 'No transactions available - Sign a message first'
                  : 'Select a transaction to verify...'
                }
              </option>
              {transactions.map((tx, index) => (
                <option key={tx.id || index} value={index}>
                  Tx {index}: "{tx.message?.substring(0, 25)}{tx.message?.length > 25 ? '...' : ''}" 
                  - {tx.signing_method} - {tx.status}
                </option>
              ))}
            </Select>
            
            {selectedTxIndex !== '' && transactions[parseInt(selectedTxIndex)] && (
              <div className="tx-preview">
                <strong>📋 Transaction Preview:</strong>
                <div>🏠 Address: {truncateHex(transactions[parseInt(selectedTxIndex)].address?.addr_hex, 16)}</div>
                <div>📝 Message: "{transactions[parseInt(selectedTxIndex)].message}"</div>
                <div>✍️ Signature: {truncateHex(transactions[parseInt(selectedTxIndex)].signature?.q_sigma_hex, 16)}</div>
                <div>📊 Status: {transactions[parseInt(selectedTxIndex)].status}</div>
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
            onClick={() => {
              console.log('Current transactions:', transactions)
            }}
            variant="secondary"
          >
            Debug Info
          </Button>
          
          <Button
            onClick={handleClearSelection}
            variant="secondary"
          >
            Clear Selection
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

export default SignatureVerification