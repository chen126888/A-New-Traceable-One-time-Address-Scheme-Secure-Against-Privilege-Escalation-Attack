import React, { useState, useCallback } from 'react'
import { Section, Button, Select, Input, DataList, Output } from './common'
import { apiService } from '../services/apiService'
import { useAppData } from '../hooks/useAppData'
import { truncateHex } from '../utils/helpers'

function MessageSigning() {
  const { 
    keys, 
    addresses, 
    loading: globalLoading, 
    error: globalError, 
    clearError,
    loadKeys,
    loadAddresses
  } = useAppData()
  
  const [message, setMessage] = useState('Hello, this is a test message!')
  const [selectedKeyIndex, setSelectedKeyIndex] = useState('')
  const [selectedAddrIndex, setSelectedAddrIndex] = useState('')
  const [selectedDSKIndex, setSelectedDSKIndex] = useState('')
  const [signingMethod, setSigningMethod] = useState('keypair') // 'keypair' or 'dsk'
  const [dskList, setDskList] = useState([])
  const [signatureList, setSignatureList] = useState([])
  const [selectedSigIndex, setSelectedSigIndex] = useState(-1)
  const [localLoading, setLocalLoading] = useState({})
  const [localError, setLocalError] = useState('')

  // 載入DSK列表
  const loadDSKList = useCallback(async () => {
    try {
      setLocalLoading(prev => ({ ...prev, loadingDSK: true }))
      const data = await apiService.get('/dsklist')
      setDskList(data)
    } catch (err) {
      setLocalError('Failed to load DSK list: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, loadingDSK: false }))
    }
  }, [])

  // 刷新數據
  const handleRefreshData = useCallback(async () => {
    setLocalError('')
    clearError()
    await Promise.all([loadKeys(), loadAddresses(), loadDSKList()])
  }, [loadKeys, loadAddresses, loadDSKList, clearError])

  // 簽名消息
  const handleSignMessage = useCallback(async () => {
    if (!message.trim()) {
      setLocalError('Please enter a message to sign!')
      return
    }

    try {
      setLocalLoading(prev => ({ ...prev, signing: true }))
      setLocalError('')
      clearError()
      
      let signature
      
      if (signingMethod === 'dsk') {
        if (selectedDSKIndex === '') {
          setLocalError('Please select a DSK!')
          return
        }
        
        signature = await apiService.signMessage(message, parseInt(selectedDSKIndex))
      } else {
        if (selectedAddrIndex === '' || selectedKeyIndex === '') {
          setLocalError('Please select both an address and a key!')
          return
        }
        
        signature = await apiService.post('/sign', {
          message: message,
          address_index: parseInt(selectedAddrIndex),
          key_index: parseInt(selectedKeyIndex)
        })
      }
      
      const signatureWithIndex = {
        ...signature,
        index: signatureList.length,
        timestamp: new Date().toISOString()
      }
      
      setSignatureList(prev => [...prev, signatureWithIndex])
      
    } catch (err) {
      setLocalError('Message signing failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, signing: false }))
    }
  }, [message, signingMethod, selectedDSKIndex, selectedAddrIndex, selectedKeyIndex, signatureList.length, clearError])

  // 點擊簽名項目
  const handleSignatureClick = useCallback((index) => {
    setSelectedSigIndex(index)
  }, [])

  const getOutputContent = () => {
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (selectedSigIndex >= 0 && signatureList[selectedSigIndex]) {
      const sig = signatureList[selectedSigIndex]
      return `🔍 Signature Details - Index ${selectedSigIndex}
📝 Message: "${sig.message}"
🛠️ Signing Method: ${sig.method}
📧 Address: ${sig.address_id || 'N/A'}
🔑 Key: ${sig.key_id || 'N/A'}
🔐 DSK: ${sig.dsk_id || 'N/A'}
📊 Status: ${sig.status}
⏰ Timestamp: ${sig.timestamp}

✍️ Signature Components:
Q_sigma (G1):
${sig.q_sigma_hex}

H (Zr):
${sig.h_hex}

${sig.dsk_hex ? `DSK (G1):
${sig.dsk_hex}` : ''}`
    }
    
    // 顯示最新簽名信息
    if (signatureList.length > 0) {
      const latestSig = signatureList[signatureList.length - 1]
      return `✅ Message Signed Successfully!
📝 Message: "${latestSig.message}"
🛠️ Method: ${latestSig.method}
✍️ Q_sigma: ${truncateHex(latestSig.q_sigma_hex)}
🔢 H: ${truncateHex(latestSig.h_hex)}
📊 Status: ${latestSig.status}`
    }
    
    return ''
  }

  const signatureItems = signatureList.map((sig, index) => ({
    id: `sig_${index}`,
    header: `Signature ${index} (${sig.method})`,
    details: [
      `Message: "${sig.message.substring(0, 30)}${sig.message.length > 30 ? '...' : ''}"`,
      `Q_sigma: ${truncateHex(sig.q_sigma_hex, 12)}`,
      `Status: ${sig.status}`
    ],
    selected: index === selectedSigIndex,
    onClick: () => handleSignatureClick(index)
  }))

  return (
    <Section title="✍️ Message Signing">
      <div className="controls">
        <label>Message to Sign:</label>
        <Input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Enter your message here..."
        />
        
        <label>Signing Method:</label>
        <Select
          value={signingMethod}
          onChange={(e) => setSigningMethod(e.target.value)}
        >
          <option value="keypair">Use Key Pair (Address + Key)</option>
          <option value="dsk">Use DSK (One-time Secret Key)</option>
        </Select>
        
        {signingMethod === 'keypair' ? (
          <>
            <label>Select Address:</label>
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
            
            <label>Select Key:</label>
            <Select
              value={selectedKeyIndex}
              onChange={(e) => setSelectedKeyIndex(e.target.value)}
            >
              <option value="">Select a key...</option>
              {keys.map((key, index) => (
                <option key={key.id} value={index}>
                  {key.id} - A: {truncateHex(key.A_hex, 8)}
                </option>
              ))}
            </Select>
          </>
        ) : (
          <>
            <label>Select DSK:</label>
            <Select
              value={selectedDSKIndex}
              onChange={(e) => setSelectedDSKIndex(e.target.value)}
            >
              <option value="">Select a DSK...</option>
              {dskList.map((dsk, index) => (
                <option key={dsk.id} value={index}>
                  {dsk.id} - For: {dsk.address_id} - {truncateHex(dsk.dsk_hex, 8)}
                </option>
              ))}
            </Select>
          </>
        )}
        
        <div className="inline-controls">
          <Button
            onClick={handleRefreshData}
            variant="secondary"
          >
            Refresh Data
          </Button>
          
          <Button
            onClick={handleSignMessage}
            loading={localLoading.signing}
            disabled={localLoading.signing || !message.trim()}
          >
            Sign Message
          </Button>
        </div>
      </div>
      
      <DataList items={signatureItems} />
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />
    </Section>
  )
}

export default MessageSigning