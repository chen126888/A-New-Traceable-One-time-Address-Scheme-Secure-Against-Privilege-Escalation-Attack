import React, { useState, useCallback } from 'react'
import { Section, Button, Select, DataList, Output } from './common'
import { apiService } from '../services/apiService'
import { useAppData } from '../hooks/useAppData'
import { truncateHex } from '../utils/helpers'

function AddressGeneration() {
  const { 
    keys, 
    addresses, 
    addAddress, 
    loadKeys, 
    loading: globalLoading, 
    error: globalError, 
    clearError 
  } = useAppData()
  
  const [selectedKeyIndex, setSelectedKeyIndex] = useState('')
  const [selectedAddrIndex, setSelectedAddrIndex] = useState(-1)
  const [localLoading, setLocalLoading] = useState({})
  const [localError, setLocalError] = useState('')

  // 使用 useCallback 防止無限循環
  const handleRefreshKeys = useCallback(async () => {
    setLocalError('')
    clearError() // 使用 clearError 而不是 setError('')
    await loadKeys()
  }, [loadKeys, clearError])

  const handleGenerateAddress = useCallback(async () => {
    if (selectedKeyIndex === '') {
      setLocalError('Please select a key!')
      return
    }

    try {
      setLocalLoading(prev => ({ ...prev, addrgen: true }))
      setLocalError('')
      clearError()
      
      const newAddress = await apiService.generateAddress(parseInt(selectedKeyIndex))
      addAddress(newAddress)
      
    } catch (err) {
      setLocalError('Address generation failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, addrgen: false }))
    }
  }, [selectedKeyIndex, addAddress, clearError])

  const handleAddressClick = useCallback((index) => {
    setSelectedAddrIndex(index)
  }, [])

  const getOutputContent = () => {
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (selectedAddrIndex >= 0 && addresses[selectedAddrIndex]) {
      const addr = addresses[selectedAddrIndex]
      return `🔍 Address Details - ${addr.id}
🆔 Index: ${selectedAddrIndex}
👤 Owner Key: ${addr.key_id} (Index: ${addr.key_index})
📊 Status: ${addr.status}

🏠 Address:
${addr.addr_hex}

🎲 R1:
${addr.r1_hex}

🎲 R2:
${addr.r2_hex}

🔒 C:
${addr.c_hex}`
    }
    
    // 顯示最新生成的地址信息
    if (addresses.length > 0) {
      const latestAddr = addresses[addresses.length - 1]
      return `✅ Address Generated Successfully!
🆔 Address ID: ${latestAddr.id}
👤 Owner Key: ${latestAddr.key_id}
🏠 Address: ${truncateHex(latestAddr.addr_hex)}
🎲 R1: ${truncateHex(latestAddr.r1_hex)}
🎲 R2: ${truncateHex(latestAddr.r2_hex)}
🔒 C: ${truncateHex(latestAddr.c_hex)}`
    }
    
    return ''
  }

  const addressItems = addresses.map((addr, index) => ({
    id: addr.id,
    header: `${addr.id} (Owner: ${addr.key_id})`,
    details: [
      `${truncateHex(addr.addr_hex, 20)}`
    ],
    selected: index === selectedAddrIndex,
    onClick: () => handleAddressClick(index)
  }))

  return (
    <Section title="📧 Address Generation">
      <div className="controls">
        <label>Select Key for Address Generation:</label>
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
            onClick={handleGenerateAddress}
            loading={localLoading.addrgen}
            disabled={selectedKeyIndex === '' || localLoading.addrgen}
          >
            Generate Address
          </Button>
          
          <Button
            onClick={handleRefreshKeys}
            variant="secondary"
          >
            Refresh Keys
          </Button>
        </div>
      </div>
      
      <DataList items={addressItems} />
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />
    </Section>
  )
}

export default AddressGeneration