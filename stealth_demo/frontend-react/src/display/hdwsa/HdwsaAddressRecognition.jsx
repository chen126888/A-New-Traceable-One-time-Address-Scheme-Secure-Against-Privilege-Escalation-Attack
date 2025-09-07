import React, { useState } from 'react'
import { Section, Button, Select, Output } from '../../components/common'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'
import { truncateHex } from '../../utils/helpers'

function HdwsaAddressRecognition() {
  const { keys, addresses, loadAllData, loading: globalLoading, error: globalError, setError } = useAppData()
  const [selectedKeyIndex, setSelectedKeyIndex] = useState('')
  const [selectedAddrIndex, setSelectedAddrIndex] = useState('')
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
      setLocalError('Please select both an address and a user wallet!')
      return
    }

    try {
      setLocalLoading(prev => ({ ...prev, recognizing: true }))
      setLocalError('')
      setError('')
      
      const result = await apiService.recognizeAddress(
        parseInt(selectedAddrIndex), 
        parseInt(selectedKeyIndex)
      )
      
      setRecognitionResult(result)
      
    } catch (err) {
      setLocalError('Address recognition failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, recognizing: false }))
    }
  }

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
    
    if (recognitionResult) {
      const selectedAddr = addresses[parseInt(selectedAddrIndex)]
      const selectedWallet = keys[parseInt(selectedKeyIndex)]
      const level = selectedWallet ? selectedWallet.full_id.split(',').length - 1 : 0
      
      return `🔍 HDWSA Address Recognition Results:
🆔 Address Index: ${recognitionResult.address_index}
🔑 Wallet Used: ${recognitionResult.wallet_id} (Level ${level})
🎯 Match Result: ${recognitionResult.is_match ? '✅ Match' : '❌ No Match'}
📊 Status: ${recognitionResult.status}
🔧 Method: ${recognitionResult.method} (HDWSA uses unified recognition)
🎯 Scheme: hdwsa

📋 Detailed Information:
🏠 Address Qr: ${truncateHex(selectedAddr?.Qr_hex)}
🔐 Address Qvk: ${truncateHex(selectedAddr?.Qvk_hex)}
🔑 Wallet A: ${truncateHex(selectedWallet?.A_hex)}
🔑 Wallet B: ${truncateHex(selectedWallet?.B_hex)}

💡 HDWSA Recognition Features:
• Unified Method: Single recognition algorithm
• Hierarchical Support: Works with all wallet levels
• API Compatible: Accepts fast/full parameters

${recognitionResult.is_match ? 
  '✅ Address belongs to this hierarchical wallet!' : 
  '❌ Address does not belong to this wallet.'}`
    }
    
    return 'Select an address and wallet, then click "Recognize Address" to test ownership.'
  }

  const keyOptions = (keys || []).map((wallet, index) => ({
    value: index,
    label: getWalletDisplayName(wallet)
  }))

  const addressOptions = (addresses || []).map((addr, index) => {
    const wallet = (keys || []).find(k => k.index === addr.key_index)
    const level = (wallet && wallet.full_id) ? wallet.full_id.split(',').length - 1 : 0
    const levelIcon = level === 0 ? '🏠' : '📁'.repeat(level)
    return {
      value: index,
      label: `${levelIcon} Address ${addr.index} (from ${addr.wallet_id})`
    }
  })

  return (
    <Section title="🎯 HDWSA Address Recognition">
      <div className="controls">
        <div className="input-group">
          <Select
            label="Select Address to Check:"
            value={selectedAddrIndex}
            onChange={(e) => setSelectedAddrIndex(e.target.value)}
            disabled={localLoading.recognizing}
          >
            <option value="">Select an address...</option>
            {addressOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>

          <Select
            label="Select User Wallet to Test:"
            value={selectedKeyIndex}
            onChange={(e) => setSelectedKeyIndex(e.target.value)}
            disabled={localLoading.recognizing}
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
            onClick={handleRecognizeAddress}
            loading={localLoading.recognizing}
            disabled={!selectedAddrIndex || !selectedKeyIndex || localLoading.recognizing}
          >
            🎯 Recognize Address
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

      {((keys || []).length === 0 || (addresses || []).length === 0) && (
        <div className="info-message">
          ℹ️ You need both user wallets and addresses to perform recognition. Generate them first.
        </div>
      )}
      
      <Output 
        content={getOutputContent()}
        isError={!!(localError || globalError)}
      />

      

      <style jsx>{`
        .controls {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
          margin-bottom: 1rem;
        }

        .input-group {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .button-group {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .method-selection {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .method-selection label {
          font-weight: bold;
          color: #495057;
        }

        .radio-group {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .radio-option {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-weight: normal;
          font-size: 14px;
        }

        .radio-option input[type="radio"] {
          margin: 0;
        }

        .method-note {
          font-size: 12px;
          color: #6c757d;
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 3px;
          padding: 0.5rem;
          margin-top: 0.25rem;
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

export default HdwsaAddressRecognition