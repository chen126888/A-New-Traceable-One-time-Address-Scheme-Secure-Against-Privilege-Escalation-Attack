import React, { useState, useCallback, useEffect } from 'react'
import { Section, Button, Select, Input, DataList, Output } from '../../components/common'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'
import { truncateHex } from '../../utils/helpers'

function StealthMessageSigning() {
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
  const [selectedAddrIndex, setSelectedAddrIndex] = useState('')
  const [selectedDSKIndex, setSelectedDSKIndex] = useState('')
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
      // Handle API response format: { dsks: [...] }
      const dsks = data?.dsks || data || []
      setDskList(Array.isArray(dsks) ? dsks : [])
    } catch (err) {
      setLocalError('Failed to load DSK list: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, loadingDSK: false }))
    }
  }, [])

  // 新增：監聽DSK更新事件
  useEffect(() => {
    const handleDSKUpdate = (event) => {
      const { newDSK, allDSKs } = event.detail
      console.log('MessageSigning received DSK update:', newDSK)
      setDskList(allDSKs)
    }

    window.addEventListener('dskUpdated', handleDSKUpdate)
    
    // 組件掛載時也載入DSK列表
    loadDSKList()

    return () => {
      window.removeEventListener('dskUpdated', handleDSKUpdate)
    }
  }, [loadDSKList])

  // 刷新數據
  const handleRefreshData = useCallback(async () => {
    setLocalError('')
    clearError()
    await Promise.all([loadKeys(), loadAddresses(), loadDSKList()])
  }, [loadKeys, loadAddresses, loadDSKList, clearError])

  // 簽名消息 - 新邏輯：選擇地址 + 任意DSK
  const handleSignMessage = useCallback(async () => {
    if (!message.trim()) {
      setLocalError('Please enter a message to sign!')
      return
    }

    // 檢查必要選項
    if (selectedAddrIndex === '') {
      setLocalError('Please select an address!')
      return
    }
    
    if (selectedDSKIndex === '') {
      setLocalError('Please select a DSK!')
      return
    }

    try {
      setLocalLoading(prev => ({ ...prev, signing: true }))
      setLocalError('')
      clearError()
      
      // 獲取選中的地址和DSK信息用於顯示
      const selectedAddress = addresses[parseInt(selectedAddrIndex)]
      const selectedDSK = dskList[parseInt(selectedDSKIndex)]
      
      // 使用新的API端點，傳遞地址索引和DSK索引
      const signature = await apiService.post('/sign_with_address_dsk', {
        message: message,
        address_index: parseInt(selectedAddrIndex),
        dsk_index: parseInt(selectedDSKIndex)
      })
      
      const signatureWithIndex = {
        ...signature,
        index: signatureList.length,
        timestamp: new Date().toISOString(),
        // 添加地址和DSK信息以便驗證和顯示
        address_index: parseInt(selectedAddrIndex),
        dsk_index: parseInt(selectedDSKIndex),
        address_info: {
          id: selectedAddress?.id,
          addr_hex: selectedAddress?.addr_hex,
          r2_hex: selectedAddress?.r2_hex,
          c_hex: selectedAddress?.c_hex
        },
        dsk_info: {
          id: selectedDSK?.id,
          for_address: selectedDSK?.address_id,
          is_correct_match: selectedDSK?.address_id === selectedAddress?.id
        }
      }
      
      setSignatureList(prev => [...prev, signatureWithIndex])
      
      // 通知Signature Verification組件有新簽名
      console.log('MessageSigning dispatching signatureCreated event:', signatureWithIndex)
      window.dispatchEvent(new CustomEvent('signatureCreated', { 
        detail: { signature: signatureWithIndex }
      }))
      
      // 不需要通知DSK組件，因為沒有生成新的DSK
      
    } catch (err) {
      setLocalError('Message signing failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, signing: false }))
    }
  }, [message, selectedDSKIndex, selectedAddrIndex, signatureList.length, clearError])

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
    header: `Signature ${index}`,
    details: [
      `Message: "${sig.message.substring(0, 30)}${sig.message.length > 30 ? '...' : ''}"`,
      `Address: ${sig.address_id || 'N/A'}`,
      `DSK: ${sig.dsk_id || 'N/A'} ${sig.dsk_for_address ? `(For: ${sig.dsk_for_address})` : ''}`,
      `Q_sigma: ${truncateHex(sig.q_sigma_hex, 12)}`,
      `Match: ${sig.match_status || 'unknown'}`,
      `Status: ${sig.status}`
    ],
    selected: index === selectedSigIndex,
    onClick: () => handleSignatureClick(index)
  }))

  return (
    <Section title="✍️ Message Signing (Stealth)">
      <div className="controls">
        <label>Message to Sign:</label>
        <Input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Enter your message here..."
        />
        
        <label>Select Address to Sign:</label>
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
        
        <label>Select DSK:</label>
        <Select
          value={selectedDSKIndex}
          onChange={(e) => setSelectedDSKIndex(e.target.value)}
        >
          <option value="">
            {dskList.length === 0 ? 'No DSKs available - Generate one first' : 'Select a DSK...'}
          </option>
          {dskList.map((dsk, index) => (
            <option key={dsk.id} value={index}>
              {dsk.id} - For: {dsk.address_id} - {truncateHex(dsk.dsk_hex, 8)}
              {selectedAddrIndex !== '' && addresses[parseInt(selectedAddrIndex)]?.id === dsk.address_id 
                ? ' ✓ (Correct match)' 
                : selectedAddrIndex !== '' 
                  ? ' ⚠️ (Wrong match - will fail verification)' 
                  : ''
              }
            </option>
          ))}
        </Select>
        
        <div className="inline-controls">
          <Button
            onClick={handleSignMessage}
            loading={localLoading.signing}
            disabled={localLoading.signing || !message.trim()}
          >
            Sign Message
          </Button>
          
          <Button
            onClick={handleRefreshData}
            variant="secondary"
          >
            Refresh Data
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

export default StealthMessageSigning