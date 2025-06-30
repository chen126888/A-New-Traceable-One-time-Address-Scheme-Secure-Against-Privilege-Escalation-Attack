import React, { useState } from 'react'
import { Section, Button, DataList, Output } from './common'
import { useAppData } from '../hooks/useAppData'
import { apiService } from '../services/apiService'
import { truncateHex } from '../utils/helpers'

function KeyManagement() {
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
      setLocalError('Key generation failed: ' + err.message)
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
    // 使用 localError 或 globalError
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (selectedKeyIndex >= 0 && keys[selectedKeyIndex]) {
      const key = keys[selectedKeyIndex]
      return `🔍 Key Details - ${key.id}
🆔 Index: ${selectedKeyIndex}
📄 Parameter File: ${key.param_file || 'Unknown'}
📊 Status: ${key.status}

🔓 Public Key A:
${key.A_hex}

🔓 Public Key B:
${key.B_hex}

🔐 Private Key a:
${key.a_hex}

🔐 Private Key b:
${key.b_hex}`
    }
    
    // 顯示最新生成的密鑰信息
    if (keys.length > 0) {
      const latestKey = keys[keys.length - 1]
      return `✅ Key Generated Successfully!
🆔 Key ID: ${latestKey.id}
🔓 Public Key A: ${truncateHex(latestKey.A_hex)}
🔓 Public Key B: ${truncateHex(latestKey.B_hex)}
🔐 Private Key a: ${truncateHex(latestKey.a_hex)}
🔐 Private Key b: ${truncateHex(latestKey.b_hex)}`
    }
    
    return ''
  }

  const keyItems = keys.map((key, index) => ({
    id: key.id,
    header: key.id,
    details: [
      `A: ${truncateHex(key.A_hex, 12)}`,
      `B: ${truncateHex(key.B_hex, 12)}`
    ],
    selected: index === selectedKeyIndex,
    onClick: () => handleKeyClick(index)
  }))

  return (
    <Section title="🔑 Key Management">
      <div className="controls">
        <Button
          onClick={handleGenerateKey}
          loading={localLoading.keygen || globalLoading.keys}
          disabled={localLoading.keygen || globalLoading.keys}
        >
          Generate New Key
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

export default KeyManagement