import React, { useState, useCallback, useEffect } from 'react'
import { Section, Button, Select, Input, DataList, Output } from './common'
import { apiService } from '../services/apiService'
import { useAppData } from '../hooks/useAppData'
import { truncateHex } from '../utils/helpers'
import { getDisplayComponent } from './displays'

function MessageSigning({ activeScheme }) {
  const { 
    keys, 
    addresses, 
    loading: globalLoading, 
    error: globalError, 
    clearError,
    loadKeys,
    loadAddresses,
    addTransaction  // 添加 addTransaction
  } = useAppData()
  
  const [message, setMessage] = useState('Hello, this is a test message!')
  const [selectedAddrIndex, setSelectedAddrIndex] = useState('')
  const [selectedDSKIndex, setSelectedDSKIndex] = useState('')
  // Stealth 簽名只能用 DSK，不需要 signing method 選項
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
      
      // 標準化 DSK 數據格式，處理不同 scheme 的差異
      const normalizedDSKs = data.map(dsk => ({
        ...dsk,
        // 確保有統一的 id 字段
        id: dsk.id || `dsk_${dsk.dsk_id ?? Date.now()}`,
        // 為 stealth DSK 添加平坦化的字段以便顯示
        dsk_hex: dsk.dsk_hex || dsk.dsk,
        // 確保有正確的 address_id 字段
        address_id: dsk.address_id || `stealth_addr_${dsk.addr_id}`,
        // 確保有 key_id 字段
        key_id: dsk.key_id
      }))
      
      setDskList(normalizedDSKs)
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
      // 重新載入 DSK 列表以確保數據格式一致
      loadDSKList()
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
      
      // Stealth 簽名只使用 DSK
      if (selectedDSKIndex === '') {
        setLocalError('Please select a DSK!')
        return
      }
      
      // 獲取選定的 DSK，使用 dsk_id 而不是 index
      const selectedDSK = dskList[parseInt(selectedDSKIndex)]
      if (!selectedDSK) {
        setLocalError('Selected DSK not found!')
        return
      }
      
      const signature = await apiService.post('/sign', {
        message: message,
        dsk_id: selectedDSK.dsk_id  // 使用 dsk_id 而不是 index
      })
      
      // 構造完整的交易 tx = (addr, R, m, σ)
      console.log('Signature API response:', signature)
      
      // 獲取對應的地址數據
      console.log('Current addresses array:', addresses)
      console.log('Signature API response details:', {
        addr_id: signature.addr_id,
        dsk_id: signature.dsk_id,
        sig_id: signature.sig_id
      })
      console.log('Signing method: DSK (stealth only)')  
      console.log('Selected indices:', {
        selectedAddrIndex,
        selectedDSKIndex
      })
      
      // 無論是 keypair 還是 DSK 簽名，都使用用戶明確選擇的 address
      let addressData = addresses[parseInt(selectedAddrIndex)]
      console.log('Using user-selected address index:', selectedAddrIndex)
      console.log('Address data:', addressData)
      
      console.log('Found address data for transaction:', addressData)
      
      if (!addressData) {
        console.warn('Address data not found, but proceeding with placeholder data for debugging')
        // 創建臨時的地址數據用於調試
        addressData = {
          addr_hex: 'unknown_address',
          r1_hex: 'unknown_r1', 
          r2_hex: 'unknown_r2',
          c_hex: 'unknown_c',
          key_id: signature.key_id || 'unknown_key',
          addr_id: signature.addr_id || 'unknown_addr_id'
        }
      }
      
      // 創建完整的交易對象
      const transaction = {
        // 交易核心數據 tx = (addr, R, m, σ)
        message: message,  // m: 訊息
        signature: {
          q_sigma_hex: signature.q_sigma_hex || signature.signature?.q_sigma?.hex,  // σ.Q_σ
          h_hex: signature.h_hex || signature.signature?.h?.hex  // σ.H
        },
        address: {
          addr_hex: addressData.addr_hex,  // addr: 簽名地址
          r1_hex: addressData.r1_hex,      // R.r1: 地址組件
          r2_hex: addressData.r2_hex,      // R.r2: 地址組件  
          c_hex: addressData.c_hex         // R.c: 地址組件
        },
        
        // 元數據
        signing_method: 'dsk',
        sig_id: signature.sig_id,
        dsk_id: signature.dsk_id,
        addr_id: signature.addr_id,
        key_id: addressData.key_id,
        scheme: activeScheme
      }
      
      // 添加到 global txlist
      const addedTransaction = addTransaction(transaction)
      console.log('Transaction added to global txlist:', addedTransaction)
      
      // 添加到本地簽名列表（用於顯示）
      const signatureForDisplay = {
        ...signature,
        method: 'dsk',
        q_sigma_hex: signature.q_sigma_hex || signature.signature?.q_sigma?.hex,
        h_hex: signature.h_hex || signature.signature?.h?.hex,
        tx_id: addedTransaction.id  // 關聯到交易 ID
      }
      
      setSignatureList(prev => [...prev, signatureForDisplay])
      
      // 通知DSK組件
      window.dispatchEvent(new CustomEvent('dskUpdated', { 
        detail: { newDSK: signatureForDisplay, allDSKs: [...dskList, signatureForDisplay] }
      }))
      
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
    // 使用 scheme-specific 的 Display 組件
    const MessageSigningDisplay = getDisplayComponent(activeScheme, 'MessageSigningDisplay')
    if (MessageSigningDisplay) {
      return MessageSigningDisplay({
        signatureList,
        selectedSignatureIndex: selectedSigIndex,
        onSignatureClick: handleSignatureClick,
        localError,
        globalError
      })
    }
    
    // fallback to default sitaiba display
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
        
        <label>Select Address to Sign For:</label>
        <Select
          value={selectedAddrIndex}
          onChange={(e) => {
            setSelectedAddrIndex(e.target.value)
            setSelectedDSKIndex('') // 重置 DSK 選擇
          }}
        >
          <option value="">Select an address...</option>
          {addresses.map((addr, index) => (
            <option key={addr.id} value={index}>
              {addr.id} - Owner: {addr.key_id} - {truncateHex(addr.addr_hex, 8)}
            </option>
          ))}
        </Select>
        
        <label>Select DSK for this Address:</label>
        <Select
          value={selectedDSKIndex}
          onChange={(e) => setSelectedDSKIndex(e.target.value)}
          disabled={selectedAddrIndex === ''}
        >
          <option value="">
            {selectedAddrIndex === '' ? 'Select an address first' : 
             'Select a DSK for this address...'}
          </option>
          {selectedAddrIndex !== '' && dskList
            .filter(dsk => {
              const selectedAddr = addresses[parseInt(selectedAddrIndex)]
              return dsk.addr_id === selectedAddr?.addr_id || 
                     dsk.address_id === selectedAddr?.id
            })
            .map((dsk, index) => (
              <option key={dsk.id} value={dskList.indexOf(dsk)}>
                {dsk.id} - {truncateHex(dsk.dsk_hex, 8)}
              </option>
            ))}
        </Select>
        
        <div className="inline-controls">
          <Button
            onClick={handleSignMessage}
            loading={localLoading.signing}
            disabled={localLoading.signing || !message.trim() || selectedAddrIndex === '' || selectedDSKIndex === ''}
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

export default MessageSigning