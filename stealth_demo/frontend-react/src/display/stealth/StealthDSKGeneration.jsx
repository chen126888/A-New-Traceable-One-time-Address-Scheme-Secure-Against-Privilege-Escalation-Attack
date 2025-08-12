import React, { useState, useCallback } from 'react'
import { Section, Button, Select, DataList, Output } from '../../components/common'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'
import { truncateHex } from '../../utils/helpers'

function StealthDSKGeneration() {
  const { 
    keys, 
    addresses, 
    loading: globalLoading, 
    error: globalError, 
    clearError,
    loadKeys,
    loadAddresses
  } = useAppData()
  
  const [selectedKeyIndex, setSelectedKeyIndex] = useState('')
  const [selectedAddrIndex, setSelectedAddrIndex] = useState('')
  const [selectedDSKIndex, setSelectedDSKIndex] = useState(-1)
  const [dskList, setDskList] = useState([])
  const [localLoading, setLocalLoading] = useState({})
  const [localError, setLocalError] = useState('')

  // 刷新數據
  const handleRefreshData = useCallback(async () => {
    setLocalError('')
    clearError()
    await Promise.all([loadKeys(), loadAddresses()])
  }, [loadKeys, loadAddresses, clearError])

  // 載入DSK列表
  const loadDSKList = useCallback(async () => {
    try {
      setLocalLoading(prev => ({ ...prev, loading: true }))
      const data = await apiService.get('/dsklist')
      // Handle API response format: { dsks: [...] }
      const dsks = data?.dsks || data || []
      setDskList(Array.isArray(dsks) ? dsks : [])
    } catch (err) {
      setLocalError('Failed to load DSK list: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, loading: false }))
    }
  }, [])

  // 新增：通知其他組件DSK更新的函數
  const notifyDSKUpdate = useCallback((newDSK) => {
    // 觸發自定義事件，讓MessageSigning組件知道有新的DSK
    window.dispatchEvent(new CustomEvent('dskUpdated', { 
      detail: { newDSK, allDSKs: [...dskList, newDSK] }
    }))
  }, [dskList])

  // 生成DSK
  const handleGenerateDSK = useCallback(async () => {
    if (selectedAddrIndex === '' || selectedKeyIndex === '') {
      setLocalError('Please select both an address and a key!')
      return
    }

    try {
      setLocalLoading(prev => ({ ...prev, generating: true }))
      setLocalError('')
      clearError()
      
      const newDSK = await apiService.generateDSK(
        parseInt(selectedAddrIndex), 
        parseInt(selectedKeyIndex)
      )
      
      setDskList(prev => [...prev, newDSK])
      
      // 通知其他組件DSK已更新
      notifyDSKUpdate(newDSK)
      
    } catch (err) {
      setLocalError('DSK generation failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, generating: false }))
    }
  }, [selectedAddrIndex, selectedKeyIndex, clearError, notifyDSKUpdate])

  // 點擊DSK項目
  const handleDSKClick = useCallback((index) => {
    setSelectedDSKIndex(index)
  }, [])

  const getOutputContent = () => {
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (selectedDSKIndex >= 0 && dskList[selectedDSKIndex]) {
      const dsk = dskList[selectedDSKIndex]
      return `🔍 DSK Details - ${dsk.id}
🆔 Index: ${selectedDSKIndex}
📧 For Address: ${dsk.address_id} (Index: ${dsk.address_index})
🔑 Using Key: ${dsk.key_id} (Index: ${dsk.key_index})
🛠️ Generation Method: ${dsk.method}
📊 Status: ${dsk.status}

🔐 DSK (One-time Secret Key):
${dsk.dsk_hex}

🏠 Target Address:
${dsk.for_address}

👤 Owner Public Key A:
${dsk.owner_A}

👤 Owner Public Key B:
${dsk.owner_B}`
    }
    
    // 顯示最新生成的DSK信息
    if (dskList.length > 0) {
      const latestDSK = dskList[dskList.length - 1]
      return `✅ DSK Generated Successfully!
🆔 DSK ID: ${latestDSK.id}
📧 For Address: ${latestDSK.address_id}
🔑 Using Key: ${latestDSK.key_id}
🛠️ Method: ${latestDSK.method}
🔐 DSK: ${truncateHex(latestDSK.dsk_hex)}`
    }
    
    return ''
  }

  const dskItems = dskList.map((dsk, index) => ({
    id: dsk.id,
    header: `${dsk.id} (For: ${dsk.address_id})`,
    details: [
      `Key: ${dsk.key_id}`,
      `Method: ${dsk.method}`,
      `DSK: ${truncateHex(dsk.dsk_hex, 16)}`
    ],
    selected: index === selectedDSKIndex,
    onClick: () => handleDSKClick(index)
  }))

  return (
    <Section title="🔐 DSK Generation (Stealth)">
      <div className="controls">
        <label>Select Address for DSK:</label>
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
        
        <label>Select Key for DSK Generation:</label>
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
        
        <div className="inline-controls">
          <Button
            onClick={handleGenerateDSK}
            loading={localLoading.generating}
            disabled={selectedAddrIndex === '' || selectedKeyIndex === '' || localLoading.generating}
          >
            Generate DSK
          </Button>
          
          <Button
            onClick={loadDSKList}
            variant="secondary"
            loading={localLoading.loading}
          >
            Load DSK List
          </Button>
          
          <Button
            onClick={handleRefreshData}
            variant="secondary"
          >
            Refresh Data
          </Button>
        </div>
      </div>
      
      <DataList items={dskItems} />
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />
    </Section>
  )
}

export default StealthDSKGeneration