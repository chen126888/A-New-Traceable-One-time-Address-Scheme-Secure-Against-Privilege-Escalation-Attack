import React, { useState } from 'react'
import { Section, Button, Select, DataList, Output } from '../../components/common'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'
import { truncateHex } from '../../utils/helpers'

function HdwsaDSKGeneration() {
  const { keys, addresses, dsks, addDsk, loadAllData, loading: globalLoading, error: globalError, setError } = useAppData()
  const [selectedAddrIndex, setSelectedAddrIndex] = useState('')
  const [selectedKeyIndex, setSelectedKeyIndex] = useState('')
  const [selectedDskIndex, setSelectedDskIndex] = useState(-1)
  const [localLoading, setLocalLoading] = useState({})
  const [localError, setLocalError] = useState('')

  const handleRefreshData = async () => {
    setLocalError('')
    setError('')
    await loadAllData()
  }

  const handleGenerateDsk = async () => {
    if (selectedAddrIndex === '' || selectedKeyIndex === '') {
      setLocalError('Please select both an address and a wallet!')
      return
    }

    try {
      setLocalLoading(prev => ({ ...prev, dskgen: true }))
      setLocalError('')
      setError('')
      
      const newDsk = await apiService.generateDSK(parseInt(selectedAddrIndex), parseInt(selectedKeyIndex))
      addDsk(newDsk)
      
    } catch (err) {
      setLocalError('DSK generation failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, dskgen: false }))
    }
  }

  const handleDskClick = (index) => {
    setSelectedDskIndex(index)
  }

  const getWalletDisplayName = (wallet) => {
    if (!wallet) return 'Unknown'
    const level = wallet.full_id.split(',').length - 1
    const levelIcon = level === 0 ? '🏠' : '📁'.repeat(level)
    return `${levelIcon} ${wallet.full_id} (Level ${level})`
  }

  const getOutputContent = () => {
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (selectedDskIndex >= 0 && dsks[selectedDskIndex]) {
      const dsk = dsks[selectedDskIndex]
      const address = addresses.find(a => a.index === dsk.address_index)
      const wallet = keys.find(k => k.index === dsk.key_index)
      const level = wallet ? wallet.full_id.split(',').length - 1 : 0
      
      return `🔍 HDWSA DSK Details - Index ${selectedDskIndex}
🆔 DSK Index: ${dsk.index}
👤 Wallet: ${dsk.wallet_id} (Level ${level})
🏠 Address Index: ${dsk.address_index}
🔑 Key Index: ${dsk.key_index}
📊 Status: ${dsk.status}

🔐 Derived Signing Key (DSK):
${dsk.dsk_hex}

📋 Associated Data:
🎯 Address Qr: ${truncateHex(address?.Qr_hex)}
🔐 Address Qvk: ${truncateHex(address?.Qvk_hex)}
🔑 Wallet A: ${truncateHex(wallet?.A_hex)}
🔑 Wallet B: ${truncateHex(wallet?.B_hex)}

📄 Parameter File: ${dsk.param_file}`
    }
    
    // 顯示最新生成的DSK信息
    if (dsks && dsks.length > 0) {
      const latestDsk = dsks[dsks.length - 1]
      return `✅ HDWSA DSK Generated Successfully!
🆔 DSK Index: ${latestDsk.index}
👤 For Wallet: ${latestDsk.wallet_id}
🏠 Address: ${latestDsk.address_index}
🔐 DSK: ${truncateHex(latestDsk.dsk_hex)}`
    }
    
    return ''
  }

  const keyOptions = (keys || []).map((wallet, index) => ({
    value: index,
    label: getWalletDisplayName(wallet)
  }))

  const addressOptions = (addresses || []).map((addr, index) => {
    const wallet = (keys || []).find(k => k.index === addr.key_index)
    const level = wallet ? wallet.full_id.split(',').length - 1 : 0
    const levelIcon = level === 0 ? '🏠' : '📁'.repeat(level)
    return {
      value: index,
      label: `${levelIcon} Address ${addr.index} (from ${addr.wallet_id})`
    }
  })

  const dskItems = (dsks || []).map((dsk, index) => {
    const wallet = (keys || []).find(k => k.index === dsk.key_index)
    const level = wallet ? wallet.full_id.split(',').length - 1 : 0
    const levelIcon = level === 0 ? '🏠' : '📁'.repeat(level)
    
    return {
      id: `dsk_${dsk.index}`,
      header: `${levelIcon} DSK ${dsk.index} (${dsk.wallet_id})`,
      details: [
        `Wallet: ${dsk.wallet_id}`,
        `Level: ${level}`,
        `Address: ${dsk.address_index}`,
        `DSK: ${truncateHex(dsk.dsk_hex, 12)}`
      ],
      selected: index === selectedDskIndex,
      onClick: () => handleDskClick(index)
    }
  })

  return (
    <Section title="🔐 HDWSA DSK Generation">
      <div className="controls">
        <div className="input-group">
          <Select
            label="Select Address:"
            value={selectedAddrIndex}
            onChange={(e) => setSelectedAddrIndex(e.target.value)}
            disabled={localLoading.dskgen}
          >
            <option value="">Select an address...</option>
            {addressOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>

          <Select
            label="Select Wallet:"
            value={selectedKeyIndex}
            onChange={(e) => setSelectedKeyIndex(e.target.value)}
            disabled={localLoading.dskgen}
          >
            <option value="">Select a wallet...</option>
            {keyOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>
        </div>

        <div className="button-group">
          <Button
            onClick={handleGenerateDsk}
            loading={localLoading.dskgen}
            disabled={!selectedAddrIndex || !selectedKeyIndex || localLoading.dskgen}
          >
            🔐 Generate DSK
          </Button>
          
          <Button
            onClick={handleRefreshData}
            variant="secondary"
            loading={globalLoading.keys || globalLoading.addresses}
          >
            🔄 Refresh Data
          </Button>
        </div>
      </div>

      {(keys.length === 0 || addresses.length === 0) && (
        <div className="info-message">
          ℹ️ You need both wallets and addresses to generate DSKs. Create them first.
        </div>
      )}
      
      <DataList items={dskItems} />
      
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

export default HdwsaDSKGeneration