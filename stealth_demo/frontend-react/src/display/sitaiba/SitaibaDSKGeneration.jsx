import React, { useState, useCallback } from 'react'
import { Section, Button, Select, DataList, Output } from '../../components/common'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'
import { truncateHex } from '../../utils/helpers'

function SitaibaDSKGeneration() {
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

  const handleRefreshData = useCallback(async () => {
    setLocalError('')
    clearError()
    await Promise.all([loadKeys(), loadAddresses()])
  }, [loadKeys, loadAddresses, clearError])

  const loadDSKList = useCallback(async () => {
    try {
      setLocalLoading(prev => ({ ...prev, loading: true }))
      const data = await apiService.get('/dsklist')
      const dsks = data?.dsks || data || []
      setDskList(Array.isArray(dsks) ? dsks : [])
    } catch (err) {
      setLocalError('Failed to load DSK list: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, loading: false }))
    }
  }, [])

  const notifyDSKUpdate = useCallback((newDSK) => {
    window.dispatchEvent(new CustomEvent('dskUpdated', { 
      detail: { newDSK, allDSKs: [...dskList, newDSK] }
    }))
  }, [dskList])

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
      notifyDSKUpdate(newDSK)
      
    } catch (err) {
      setLocalError('SITAIBA DSK generation failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, generating: false }))
    }
  }, [selectedAddrIndex, selectedKeyIndex, clearError, notifyDSKUpdate])

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
      return `🔍 SITAIBA DSK Details - ${dsk.id}
🆔 Index: ${selectedDSKIndex}
📧 Corresponding Address: ${dsk.address_id} (Index: ${dsk.address_index})
🔑 Key Used: ${dsk.key_id} (Index: ${dsk.key_index})
🎯 Scheme: ${dsk.scheme || 'sitaiba'}
📊 Status: ${dsk.status}

🔐 DSK (Zr Group Element):
${dsk.dsk_hex}

🏠 Corresponding Address:
${dsk.for_address}

👤 Owner Public Key:
A: ${dsk.owner_A}
B: ${dsk.owner_B}

💡 SITAIBA DSK Features:
• DSK belongs to Zr group (unlike Stealth's G1 group)
• Cannot be used for message signing (SITAIBA doesn't support signing)
• Can be used to verify address ownership`
    }
    
    if (dskList.length > 0) {
      const latestDSK = dskList[dskList.length - 1]
      return `✅ SITAIBA DSK Generated Successfully!
🆔 DSK ID: ${latestDSK.id}
🎯 Scheme: SITAIBA
📧 Corresponding Address: ${latestDSK.address_id}
🔑 Key Used: ${latestDSK.key_id}
🔐 DSK (Zr Group): ${truncateHex(latestDSK.dsk_hex)}

`
    }
    
    return ''
  }

  const dskItems = dskList.map((dsk, index) => ({
    id: dsk.id,
    header: `${dsk.id} (Address: ${dsk.address_id})`,
    details: [
      `DSK: ${truncateHex(dsk.dsk_hex, 12)}`,
      `Key: ${dsk.key_id}`,
      `Scheme: ${dsk.scheme || 'sitaiba'}`
    ],
    selected: index === selectedDSKIndex,
    onClick: () => handleDSKClick(index)
  }))

  return (
    <Section title="🔐 DSK Generation (SITAIBA)">
      <div className="controls">
        <label>Select Address:</label>
        <Select
          value={selectedAddrIndex}
          onChange={(e) => setSelectedAddrIndex(e.target.value)}
          disabled={globalLoading.all}
        >
          <option value="">Select address...</option>
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
          disabled={globalLoading.all}
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
            onClick={handleGenerateDSK}
            loading={localLoading.generating}
            disabled={selectedAddrIndex === '' || selectedKeyIndex === '' || localLoading.generating}
          >
            Generate DSK
          </Button>
          
          <Button
            onClick={handleRefreshData}
            variant="secondary"
            disabled={globalLoading.all}
          >
            Refresh Data
          </Button>
          
          <Button
            onClick={loadDSKList}
            variant="secondary"
            loading={localLoading.loading}
            disabled={localLoading.loading}
          >
            Load DSK List
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

export default SitaibaDSKGeneration