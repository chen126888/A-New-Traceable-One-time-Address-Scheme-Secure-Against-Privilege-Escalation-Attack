import React, { useState, useCallback } from 'react'
import { Section, Button, Select, DataList, Output } from '../../components/common'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'
import { truncateHex } from '../../utils/helpers'

function SitaibaAddressGeneration() {
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

  const handleRefreshKeys = useCallback(async () => {
    setLocalError('')
    clearError()
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
      setLocalError('SITAIBA address generation failed: ' + err.message)
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
      return `🔍 SITAIBA Address Details - ${addr.id}
🆔 Index: ${selectedAddrIndex}
👤 Owner Key: ${addr.key_id} (Index: ${addr.key_index})
🎯 Scheme: ${addr.scheme || 'sitaiba'}
📊 Status: ${addr.status}

🏠 Address (G1 Group):
${addr.addr_hex}

🎲 Random Parameter R1 (G1 Group):
${addr.r1_hex}

🎲 Random Parameter R2 (G1 Group):
${addr.r2_hex}

💡 SITAIBA Address Features:
• Address and random parameters are in G1 group
• Supports fast and full address recognition
• Address can be used for DSK generation and identity tracing
• No C parameter required (unlike Stealth)`
    }
    
    if (addresses.length > 0) {
      const latestAddr = addresses[addresses.length - 1]
      return `✅ SITAIBA Address Generated Successfully!
🆔 Address ID: ${latestAddr.id}
🎯 Scheme: SITAIBA
👤 Owner Key: ${latestAddr.key_id}
🏠 Address: ${truncateHex(latestAddr.addr_hex)}
🎲 R1: ${truncateHex(latestAddr.r1_hex)}
🎲 R2: ${truncateHex(latestAddr.r2_hex)}

`
    }
    
    return ''
  }

  const addressItems = addresses.map((addr, index) => ({
    id: addr.id,
    header: `${addr.id} (Owner: ${addr.key_id})`,
    details: [
      `${truncateHex(addr.addr_hex, 20)}`,
      `Scheme: ${addr.scheme || 'sitaiba'}`
    ],
    selected: index === selectedAddrIndex,
    onClick: () => handleAddressClick(index)
  }))

  return (
    <Section title="📧 Address Generation (SITAIBA)">
      <div className="controls">
        <label>Select Key for Address Generation:</label>
        <Select
          value={selectedKeyIndex}
          onChange={(e) => setSelectedKeyIndex(e.target.value)}
        >
          <option value="">Select key...</option>
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

export default SitaibaAddressGeneration