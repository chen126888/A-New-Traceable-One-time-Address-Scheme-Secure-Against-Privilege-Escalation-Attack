import React, { useState } from 'react'
import { Section, Button, DataList, Output } from '../../components/common'
import { useAppData } from '../../hooks/useAppData'
import { apiService } from '../../services/apiService'
import { truncateHex } from '../../utils/helpers'

function SitaibaKeyManagement() {
  const { keys, addKey, loadKeys, loading: globalLoading, error: globalError, setError } = useAppData()
  const [selectedKeyIndex, setSelectedKeyIndex] = useState(-1)
  const [localLoading, setLocalLoading] = useState({})
  const [localError, setLocalError] = useState('')

  const handleGenerateKey = async () => {
    try {
      setLocalLoading(prev => ({ ...prev, keygen: true }))
      setLocalError('')
      setError('')
      
      const newKey = await apiService.generateKey()
      addKey(newKey)
      
    } catch (err) {
      setLocalError('SITAIBA key generation failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, keygen: false }))
    }
  }

  const handleRefreshKeys = async () => {
    setLocalError('')
    setError('')
    await loadKeys()
  }

  const handleKeyClick = (index) => {
    setSelectedKeyIndex(index)
  }

  const getOutputContent = () => {
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (selectedKeyIndex >= 0 && keys[selectedKeyIndex]) {
      const key = keys[selectedKeyIndex]
      return `🔍 SITAIBA Key Details - ${key.id}
🆔 Index: ${selectedKeyIndex}
📄 Parameter File: ${key.param_file || 'Unknown'}
🎯 Scheme: ${key.scheme || 'sitaiba'}
📊 Status: ${key.status}

🔓 Public Key A (G1 Group):
${key.A_hex}

🔓 Public Key B (G1 Group):
${key.B_hex}

🔐 Private Key a (Zr Group):
${key.a_hex}

🔐 Private Key b (Zr Group):
${key.b_hex}

💡 SITAIBA Features:
• Private keys a, b belong to Zr group
• Public keys A, B belong to G1 group
• Supports fast and full address recognition
• Does not support message signing functionality`
    }
    
    // Display latest generated key information
    if (keys.length > 0) {
      const latestKey = keys[keys.length - 1]
      return `✅ SITAIBA Key Generation Successful!
🆔 Key ID: ${latestKey.id}
🎯 Scheme: SITAIBA
🔓 Public Key A: ${truncateHex(latestKey.A_hex)}
🔓 Public Key B: ${truncateHex(latestKey.B_hex)}
🔐 Private Key a: ${truncateHex(latestKey.a_hex)}
🔐 Private Key b: ${truncateHex(latestKey.b_hex)}

`
    }
    
    return ''
  }

  const keyItems = keys.map((key, index) => ({
    id: key.id,
    header: `${key.id} (SITAIBA)`,
    details: [
      `A: ${truncateHex(key.A_hex, 12)}`,
      `B: ${truncateHex(key.B_hex, 12)}`,
      `Scheme: ${key.scheme || 'sitaiba'}`
    ],
    selected: index === selectedKeyIndex,
    onClick: () => handleKeyClick(index)
  }))

  return (
    <Section title="🔑 Key Management (SITAIBA)">
      <div className="controls">
        <Button
          onClick={handleGenerateKey}
          loading={localLoading.keygen || globalLoading.keys}
          disabled={localLoading.keygen || globalLoading.keys}
        >
          Generate Key
        </Button>
        <Button
          onClick={handleRefreshKeys}
          variant="secondary"
        >
          Refresh Key List
        </Button>
      </div>
      
      <DataList items={keyItems} />
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />
    </Section>
  )
}

export default SitaibaKeyManagement