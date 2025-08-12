import React, { useState } from 'react'
import { Section, Button, Select, Output } from '../../components/common'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'
import { truncateHex } from '../../utils/helpers'

function SitaibaAddressRecognition() {
  const { keys, addresses, loadAllData, loading: globalLoading, error: globalError, setError } = useAppData()
  const [selectedKeyIndex, setSelectedKeyIndex] = useState('')
  const [selectedAddrIndex, setSelectedAddrIndex] = useState('')
  const [recognitionMethod, setRecognitionMethod] = useState('fast') // fast or full for SITAIBA
  const [localLoading, setLocalLoading] = useState({})
  const [localError, setLocalError] = useState('')
  const [recognitionResult, setRecognitionResult] = useState(null)

  const handleRefreshData = async () => {
    setLocalError('')
    setError('')
    setRecognitionResult(null)
    await loadAllData()
  }

  const handleRecognizeAddress = async () => {
    if (selectedAddrIndex === '' || selectedKeyIndex === '') {
      setLocalError('Please select both an address and a key!')
      return
    }

    try {
      setLocalLoading(prev => ({ ...prev, recognizing: true }))
      setLocalError('')
      setError('')
      
      const result = await apiService.recognizeAddress(
        parseInt(selectedAddrIndex), 
        parseInt(selectedKeyIndex),
        recognitionMethod === 'fast'
      )
      
      setRecognitionResult(result)
      
    } catch (err) {
      setLocalError('SITAIBA address recognition failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, recognizing: false }))
    }
  }

  const getOutputContent = () => {
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (recognitionResult) {
      const selectedAddr = addresses[parseInt(selectedAddrIndex)]
      const selectedKey = keys[parseInt(selectedKeyIndex)]
      
      return `🔍 SITAIBA Address Recognition Result:
📧 Address: ${recognitionResult.address_id}
🔑 Key Used: ${recognitionResult.key_id}
👤 Is Owner: ${recognitionResult.is_owner ? '✅ Yes' : '❌ No'}
✅ Recognition Result: ${recognitionResult.recognized ? '✅ Recognized' : '❌ Not Recognized'}
🔧 Recognition Method: ${recognitionResult.method}
📊 Status: ${recognitionResult.status}
🎯 Scheme: ${recognitionResult.scheme || 'sitaiba'}

📋 Detailed Information:
🏠 Address: ${truncateHex(selectedAddr?.addr_hex)}
🔑 Key A: ${truncateHex(selectedKey?.A_hex)}
🔑 Key B: ${truncateHex(selectedKey?.B_hex)}

💡 SITAIBA Recognition Features:
• Fast Recognition: Uses only r1, r2, A, a parameters
• Full Recognition: Uses all parameters for recognition

`
    }
    
    return ''
  }

  return (
    <Section title="🔍 Address Recognition (SITAIBA)">
      <div className="controls">
        <label>Select Address to Recognize:</label>
        <Select
          value={selectedAddrIndex}
          onChange={(e) => setSelectedAddrIndex(e.target.value)}
          disabled={globalLoading.all}
        >
          <option value="">
            {globalLoading.all ? 'Loading addresses...' : 'Select address...'}
          </option>
          {addresses.map((addr, index) => (
            <option key={addr.id} value={index}>
              {addr.id} - Owner: {addr.key_id} - {truncateHex(addr.addr_hex, 8)}
            </option>
          ))}
        </Select>
        
        <label>Select Key for Recognition:</label>
        <Select
          value={selectedKeyIndex}
          onChange={(e) => setSelectedKeyIndex(e.target.value)}
          disabled={globalLoading.all}
        >
          <option value="">
            {globalLoading.all ? 'Loading keys...' : 'Select key...'}
          </option>
          {keys.map((key, index) => (
            <option key={key.id} value={index}>
              {key.id} - A: {truncateHex(key.A_hex, 8)}
            </option>
          ))}
        </Select>
        
        <label>Recognition Method:</label>
        <Select
          value={recognitionMethod}
          onChange={(e) => setRecognitionMethod(e.target.value)}
          disabled={globalLoading.all}
        >
          <option value="fast">Fast Recognition</option>
          <option value="full">Full Recognition</option>
        </Select>
        
        <div className="inline-controls">
          <Button
            onClick={handleRecognizeAddress}
            loading={localLoading.recognizing}
            disabled={selectedAddrIndex === '' || selectedKeyIndex === '' || localLoading.recognizing}
          >
            Recognize Address
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

export default SitaibaAddressRecognition