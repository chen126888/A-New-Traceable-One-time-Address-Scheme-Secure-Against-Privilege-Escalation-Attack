import React, { useState } from 'react'
import { Section, Button, Select, Input, DataList, Output } from '../../components/common'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'
import { truncateHex } from '../../utils/helpers'

function HdwsaMessageSigning() {
  const { dsks, txMessages, addTxMessage, loadAllData, loading: globalLoading, error: globalError, setError } = useAppData()
  const [selectedDskIndex, setSelectedDskIndex] = useState('')
  const [message, setMessage] = useState('')
  const [selectedSigIndex, setSelectedSigIndex] = useState(-1)
  const [localLoading, setLocalLoading] = useState({})
  const [localError, setLocalError] = useState('')

  const handleRefreshData = async () => {
    setLocalError('')
    setError('')
    await loadAllData()
  }

  const handleSignMessage = async () => {
    if (selectedDskIndex === '' || !message.trim()) {
      setLocalError('Please select a DSK and enter a message!')
      return
    }

    try {
      setLocalLoading(prev => ({ ...prev, signing: true }))
      setLocalError('')
      setError('')
      
      console.log('Raw selectedDskIndex:', selectedDskIndex);
      const signature = await apiService.signMessage({
        message: message.trim(),
        dsk_index: parseInt(selectedDskIndex)
      })
      
      addTxMessage(signature)
      setMessage('')
      
    } catch (err) {
      setLocalError('Message signing failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, signing: false }))
    }
  }

  const handleSigClick = (index) => {
    setSelectedSigIndex(index)
  }

  const getOutputContent = () => {
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (selectedSigIndex >= 0 && txMessages && txMessages[selectedSigIndex]) {
      const signature = txMessages[selectedSigIndex]
      const dsk = (dsks || []).find(d => d.index === signature.dsk_index)
      
      return `🔍 HDWSA Signature Details - ${signature.id}
🆔 Signature Index: ${signature.index}
👤 Wallet: ${signature.wallet_id}
🔐 DSK Used: ${signature.dsk_index}
🏠 Address: ${signature.address_index}
📊 Status: ${signature.status}

💬 Signed Message:
"${signature.message}"

✍️ Signature Components:
🔒 h (Zr element):
${signature.h_hex}

🎯 Q_sigma (G1 element):
${signature.Q_sigma_hex}

📋 DSK Information:
🔐 DSK: ${truncateHex(dsk?.dsk_hex)}
👤 DSK Wallet: ${dsk?.wallet_id}

📄 Parameter File: ${signature.param_file}`
    }
    
    // 顯示最新簽名信息
    if (txMessages && txMessages.length > 0) {
      const latestSig = txMessages[txMessages.length - 1]
      return `✅ HDWSA Message Signed Successfully!
🆔 Signature ID: ${latestSig.id}
👤 Wallet: ${latestSig.wallet_id}
💬 Message: "${latestSig.message}"
🔒 h: ${truncateHex(latestSig.h_hex)}
🎯 Q_sigma: ${truncateHex(latestSig.Q_sigma_hex)}`
    }
    
    return ''
  }

  const dskOptions = (dsks || []).map((dsk, index) => {
    const level = dsk.wallet_id.split(',').length - 1
    const levelIcon = level === 0 ? '🏠' : '📁'.repeat(level)
    return {
      value: index,
      label: `${levelIcon} DSK ${dsk.index} (${dsk.wallet_id})`
    }
  })

  const signatureItems = (txMessages || []).map((sig, index) => {
    const level = sig.wallet_id.split(',').length - 1
    const levelIcon = level === 0 ? '🏠' : '📁'.repeat(level)
    
    return {
      id: sig.id,
      header: `${levelIcon} ${sig.id} (${sig.wallet_id})`,
      details: [
        `Wallet: ${sig.wallet_id}`,
        `Level: ${level}`,
        `Message: "${sig.message.substring(0, 30)}${sig.message.length > 30 ? '...' : ''}"`,
        `h: ${truncateHex(sig.h_hex, 12)}`
      ],
      selected: index === selectedSigIndex,
      onClick: () => handleSigClick(index)
    }
  })

  return (
    <Section title="✍️ HDWSA Message Signing">
      <div className="controls">
        <div className="input-group">
          <Select
            label="Select DSK:"
            value={selectedDskIndex}
            onChange={(e) => setSelectedDskIndex(e.target.value)}
            disabled={localLoading.signing}
          >
            <option value="">Select a DSK...</option>
            {dskOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>

          <Input
            label="Message to Sign:"
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Enter your message here..."
            disabled={localLoading.signing}
          />
        </div>

        <div className="button-group">
          <Button
            onClick={handleSignMessage}
            loading={localLoading.signing}
            disabled={selectedDskIndex === '' || !message.trim() || localLoading.signing}
          >
            ✍️ Sign Message
          </Button>
          
          <Button
            onClick={handleRefreshData}
            variant="secondary"
            loading={globalLoading.dsks}
          >
            🔄 Refresh DSKs
          </Button>
        </div>
      </div>

      {(dsks || []).length === 0 && (
        <div className="info-message">
          ℹ️ No DSKs available. Please generate DSKs first.
        </div>
      )}
      
      <DataList items={signatureItems} />
      
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

export default HdwsaMessageSigning