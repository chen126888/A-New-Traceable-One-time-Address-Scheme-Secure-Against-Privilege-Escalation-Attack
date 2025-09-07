import React, { useState, useCallback } from 'react'
import { Section, Button, Select, DataList, Output } from '../../components/common'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'
import { truncateHex } from '../../utils/helpers'

function HdwsaAddressGeneration() {
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
      setLocalError('Please select a user wallet!')
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

  const getWalletDisplayName = (wallet) => {
    if (!wallet || !wallet.full_id) return 'Unknown Wallet'
    const level = wallet.full_id.split(',').length - 1
    const levelIcon = level === 0 ? '🏠' : '📁'.repeat(level)
    return `${levelIcon} ${wallet.full_id} (Level ${level})`
  }

  const getOutputContent = () => {
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (selectedAddrIndex >= 0 && addresses && addresses[selectedAddrIndex]) {
      const address = addresses[selectedAddrIndex]
      const wallet = (keys || []).find(k => k.index === address.key_index)
      return `🔍 HDWSA Address Details - Index ${address.index}
🆔 Address Index: ${address.index}
👤 From Wallet: ${address.wallet_id}
🔑 Key Index: ${address.key_index}
📊 Status: ${address.status}

🎯 Address Qr:
${address.Qr_hex}

🔐 Address Qvk:
${address.Qvk_hex}

📄 Parameter File: ${address.param_file}`
    }
    
    // 顯示最新生成的地址信息
    if (addresses && addresses.length > 0) {
      const latestAddr = addresses[addresses.length - 1]
      const wallet = (keys || []).find(k => k.index === latestAddr.key_index)
      return `✅ HDWSA Address Generated Successfully!
🆔 Address Index: ${latestAddr.index}
👤 From Wallet: ${latestAddr.wallet_id}
🎯 Qr: ${truncateHex(latestAddr.Qr_hex)}
🔐 Qvk: ${truncateHex(latestAddr.Qvk_hex)}`
    }
    
    return ''
  }

  const keyOptions = (keys || []).map((wallet, index) => ({
    value: index,
    label: getWalletDisplayName(wallet)
  }))

  const addressItems = (addresses || []).map((addr, index) => {
    const wallet = (keys || []).find(k => k.index === addr.key_index)
    const level = (wallet && wallet.full_id) ? wallet.full_id.split(',').length - 1 : 0
    const levelIcon = level === 0 ? '🏠' : '📁'.repeat(level)
    
    return {
      id: `addr_${addr.index}`,
      header: `${levelIcon} Address ${addr.index} (from ${addr.wallet_id})`,
      details: [
        `Wallet: ${addr.wallet_id}`,
        `Level: ${level}`,
        `Qr: ${truncateHex(addr.Qr_hex, 12)}`,
        `Qvk: ${truncateHex(addr.Qvk_hex, 12)}`
      ],
      selected: index === selectedAddrIndex,
      onClick: () => handleAddressClick(index)
    }
  })

  return (
    <Section title="📍 HDWSA Address Generation">
      <div className="controls">
        <div className="input-group">
          <Select
            label="Select User Wallet:"
            value={selectedKeyIndex}
            onChange={(e) => setSelectedKeyIndex(e.target.value)}
            disabled={localLoading.addrgen || globalLoading.keys}
          >
            <option value="">Select a user wallet...</option>
            {keyOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>
        </div>

        <div className="button-group">
          <Button
            onClick={handleGenerateAddress}
            loading={localLoading.addrgen}
            disabled={!selectedKeyIndex || localLoading.addrgen || globalLoading.keys}
          >
            🎯 Generate Address
          </Button>
          
          <Button
            onClick={handleRefreshKeys}
            variant="secondary"
            loading={globalLoading.keys}
          >
            🔄 Refresh Wallets
          </Button>
        </div>
      </div>

      {keys.length === 0 && (
        <div className="info-message">
          ℹ️ No user wallets available. Please generate wallets first in Key Management.
        </div>
      )}
      
      <DataList items={addressItems} />
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />

      

      <style jsx>{`
        .controls {
          display: flex;
          flex-direction: column;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .input-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .button-group {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .info-message {
          background: #fff3cd;
          border: 1px solid #ffeaa7;
          color: #856404;
          padding: 0.75rem;
          border-radius: 4px;
          margin-bottom: 1rem;
          font-size: 14px;
        }

        .hdwsa-info {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 4px;
          padding: 1rem;
          margin-top: 1rem;
        }

        .hdwsa-info h4 {
          margin: 0 0 0.75rem 0;
          color: #495057;
          font-size: 14px;
        }

        .info-content p {
          margin: 0.5rem 0;
          font-size: 13px;
          line-height: 1.4;
          color: #6c757d;
        }

        .info-content strong {
          color: #495057;
        }
      `}</style>
    </Section>
  )
}

export default HdwsaAddressGeneration