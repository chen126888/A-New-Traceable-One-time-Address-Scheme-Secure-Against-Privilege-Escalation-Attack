import React, { useState, useEffect } from 'react'
import { Section, Button, Select, DataList, Output } from './common'
import { apiService } from '../services/apiService'
import { truncateHex } from '../utils/helpers'

function AddressGeneration() {
  const [keys, setKeys] = useState([])
  const [addresses, setAddresses] = useState([])
  const [selectedKeyIndex, setSelectedKeyIndex] = useState('')
  const [selectedAddrIndex, setSelectedAddrIndex] = useState(-1)
  const [loading, setLoading] = useState({})
  const [error, setError] = useState('')

  // 載入密鑰列表
  useEffect(() => {
    loadKeys()
  }, [])

  const loadKeys = async () => {
    try {
      const keyData = await apiService.getKeys()
      setKeys(keyData)
    } catch (err) {
      setError('Failed to load keys: ' + err.message)
    }
  }

  const handleRefreshKeys = async () => {
    setError('')
    await loadKeys()
  }

  const handleGenerateAddress = async () => {
    if (selectedKeyIndex === '') {
      setError('Please select a key!')
      return
    }

    try {
      setLoading(prev => ({ ...prev, addrgen: true }))
      setError('')
      
      const newAddress = await apiService.generateAddress(parseInt(selectedKeyIndex))
      setAddresses(prev => [...prev, newAddress])
      
    } catch (err) {
      setError('Address generation failed: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, addrgen: false }))
    }
  }

  const handleAddressClick = (index) => {
    setSelectedAddrIndex(index)
  }

  const getOutputContent = () => {
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
        
        <Button
          onClick={handleRefreshKeys}
          variant="secondary"
        >
          Refresh Keys
        </Button>
        
        <Button
          onClick={handleGenerateAddress}
          loading={loading.addrgen}
          disabled={selectedKeyIndex === '' || loading.addrgen}
        >
          Generate Address
        </Button>
      </div>
      
      <DataList items={addressItems} />
      
      <Output 
        content={getOutputContent()}
        isError={!!error}
      />
    </Section>
  )
}

export default AddressGeneration