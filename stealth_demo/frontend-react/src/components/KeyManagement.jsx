import React, { useState, useEffect } from 'react'
import { Section, Button, DataList, Output } from './common'
import { apiService } from '../services/apiService'
import { truncateHex } from '../utils/helpers'

function KeyManagement() {
  const [keys, setKeys] = useState([])
  const [selectedKeyIndex, setSelectedKeyIndex] = useState(-1)
  const [loading, setLoading] = useState({})
  const [error, setError] = useState('')

  // 載入密鑰列表
  useEffect(() => {
    loadKeyList()
  }, [])

  const loadKeyList = async () => {
    try {
      const keyData = await apiService.getKeys()
      setKeys(keyData)
    } catch (err) {
      setError('Failed to load keys: ' + err.message)
    }
  }

  const handleGenerateKey = async () => {
    try {
      setLoading(prev => ({ ...prev, keygen: true }))
      setError('')
      
      const newKey = await apiService.generateKey()
      setKeys(prev => [...prev, newKey])
      
    } catch (err) {
      setError('Key generation failed: ' + err.message)
    } finally {
      setLoading(prev => ({ ...prev, keygen: false }))
    }
  }

  const handleRefreshKeys = async () => {
    setError('')
    await loadKeyList()
  }

  const handleKeyClick = (index) => {
    setSelectedKeyIndex(index)
  }

  const getOutputContent = () => {
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
          loading={loading.keygen}
          disabled={loading.keygen}
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
        isError={!!error}
      />
    </Section>
  )
}

export default KeyManagement