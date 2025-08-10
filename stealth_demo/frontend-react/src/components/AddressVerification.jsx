import React, { useState } from 'react'
import { Section, Button, Select, Output } from './common'
import { apiService } from '../services/apiService'
import { useAppData } from '../hooks/useAppData'
import { truncateHex } from '../utils/helpers'
import { getDisplayComponent } from './displays'

function AddressVerification({ activeScheme }) {
  const { keys, addresses, loadAllData, loading: globalLoading, error: globalError, setError } = useAppData()
  const [selectedKeyIndex, setSelectedKeyIndex] = useState('')
  const [selectedAddrIndex, setSelectedAddrIndex] = useState('')
  const [localLoading, setLocalLoading] = useState({})
  const [localError, setLocalError] = useState('')
  const [verificationResult, setVerificationResult] = useState(null)

  const handleRefreshData = async () => {
    setLocalError('')
    setError('')
    setVerificationResult(null)
    await loadAllData()
  }

  const handleVerifyAddress = async () => {
    if (selectedAddrIndex === '' || selectedKeyIndex === '') {
      setLocalError('Please select both an address and a key!')
      return
    }

    try {
      setLocalLoading(prev => ({ ...prev, verifying: true }))
      setLocalError('')
      setError('')
      
      const result = await apiService.verifyAddress(
        parseInt(selectedAddrIndex), 
        parseInt(selectedKeyIndex)
      )
      
      setVerificationResult(result)
      
    } catch (err) {
      setLocalError('Address verification failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, verifying: false }))
    }
  }

  const getOutputContent = () => {
    // 使用 scheme-specific 的 Display 組件
    const AddressVerificationDisplay = getDisplayComponent(activeScheme, 'AddressVerificationDisplay')
    if (AddressVerificationDisplay) {
      return AddressVerificationDisplay({
        verificationResult,
        addresses,
        keys,
        selectedAddrIndex,
        selectedKeyIndex,
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
      const selectedAddr = addresses[parseInt(selectedAddrIndex)]
      const selectedKey = keys[parseInt(selectedKeyIndex)]
      
      return `🔍 Address Verification Results:
📧 Address: ${verificationResult.address_id}
🔑 Key Used: ${verificationResult.key_id}
👤 Is Owner: ${verificationResult.is_owner ? '✅ Yes' : '❌ No'}
✅ Verification Result: ${verificationResult.valid ? '✅ Valid' : '❌ Invalid'}
📊 Status: ${verificationResult.status}

📋 Details:
🏠 Address: ${truncateHex(selectedAddr?.addr_hex)}
🔑 Key A: ${truncateHex(selectedKey?.A_hex)}
🔑 Key B: ${truncateHex(selectedKey?.B_hex)}

${verificationResult.is_owner && verificationResult.valid ? 
  '🎉 Perfect match! This key is the owner of this address.' : 
  verificationResult.valid ? 
    '✅ Address is valid but not owned by this key.' :
    '❌ Address verification failed.'
}`
    }
    
    return ''
  }

  return (
    <Section title="🔍 Address Verification">
      <div className="controls">
        <label>Select Address to Verify:</label>
        <Select
          value={selectedAddrIndex}
          onChange={(e) => setSelectedAddrIndex(e.target.value)}
          disabled={globalLoading.all}
        >
          <option value="">
            {globalLoading.all ? 'Loading addresses...' : 'Select an address...'}
          </option>
          {addresses.map((addr, index) => (
            <option key={addr.id} value={index}>
              {addr.id} - Owner: {addr.key_id} - {truncateHex(addr.addr_hex, 8)}
            </option>
          ))}
        </Select>
        
        <label>Select Key for Verification:</label>
        <Select
          value={selectedKeyIndex}
          onChange={(e) => setSelectedKeyIndex(e.target.value)}
          disabled={globalLoading.all}
        >
          <option value="">
            {globalLoading.all ? 'Loading keys...' : 'Select a key...'}
          </option>
          {keys.map((key, index) => (
            <option key={key.id} value={index}>
              {key.id} - A: {truncateHex(key.A_hex, 8)}
            </option>
          ))}
        </Select>
        
        <div className="inline-controls">
          <Button
            onClick={handleVerifyAddress}
            loading={localLoading.verifying}
            disabled={selectedAddrIndex === '' || selectedKeyIndex === '' || localLoading.verifying}
          >
            Verify Address
          </Button>
          
          <Button
            onClick={handleRefreshData}
            variant="secondary"
            disabled={globalLoading.all}
          >
            Refresh Data
          </Button>
        </div>
      </div>
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />
    </Section>
  )
}

export default AddressVerification