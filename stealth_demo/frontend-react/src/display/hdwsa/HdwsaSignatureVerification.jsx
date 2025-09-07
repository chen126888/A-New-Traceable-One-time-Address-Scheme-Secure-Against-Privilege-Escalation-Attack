import React, { useState } from 'react'
import { Section, Button, Select, Input, Output } from '../../components/common'
import { apiService } from '../../services/apiService'
import { useAppData } from '../../hooks/useAppData'
import { truncateHex } from '../../utils/helpers'

function HdwsaSignatureVerification() {
  const { addresses, txMessages, loadAllData, loading: globalLoading, error: globalError, setError } = useAppData()
  const [selectedSigIndex, setSelectedSigIndex] = useState('')
  const [customMessage, setCustomMessage] = useState('')
  const [useCustomMessage, setUseCustomMessage] = useState(false)
  const [localLoading, setLocalLoading] = useState({})
  const [localError, setLocalError] = useState('')
  const [verificationResult, setVerificationResult] = useState(null)

  const handleRefreshData = async () => {
    setLocalError('')
    setError('')
    setVerificationResult(null)
    await loadAllData()
  }

  const handleVerifySignature = async () => {
    if (selectedSigIndex === '') {
      setLocalError('Please select a signature!')
      return
    }

    if (useCustomMessage && !customMessage.trim()) {
      setLocalError('Please enter a custom message!')
      return
    }

    try {
      setLocalLoading(prev => ({ ...prev, verifying: true }))
      setLocalError('')
      setError('')
      
      const signature = txMessages[parseInt(selectedSigIndex)]
      const address = addresses.find(a => a.index === signature.address_index)
      
      const result = await apiService.verifySignature({
        message: useCustomMessage ? customMessage.trim() : signature.message,
        q_sigma_hex: signature.Q_sigma_hex,
        h_hex: signature.h_hex,
        address_index: signature.address_index
      })
      
      setVerificationResult(result)
      
    } catch (err) {
      setLocalError('Signature verification failed: ' + err.message)
    } finally {
      setLocalLoading(prev => ({ ...prev, verifying: false }))
    }
  }

  const getOutputContent = () => {
    const error = localError || globalError
    if (error) {
      return `Error: ${error}`
    }
    
    if (verificationResult && txMessages) {
      const signature = txMessages[parseInt(selectedSigIndex)]
      const address = (addresses || []).find(a => a.index === signature.address_index)
      
      return `🔍 HDWSA Signature Verification Results:
🆔 Signature: ${signature.id}
👤 Wallet: ${verificationResult.wallet_id}
✅ Is Valid: ${verificationResult.is_valid ? '✅ Valid' : '❌ Invalid'}
📊 Status: ${verificationResult.status}

💬 Verified Message:
"${verificationResult.message}"

💬 Original Message:
"${verificationResult.original_message}"

📋 Signature Details:
🔒 h: ${truncateHex(signature.h_hex)}
🎯 Q_sigma: ${truncateHex(signature.Q_sigma_hex)}

📋 Address Information:
🎯 Address Qr: ${truncateHex(address?.Qr_hex)}
🔐 Address Qvk: ${truncateHex(address?.Qvk_hex)}

${verificationResult.is_valid ? 
  '✅ Signature is cryptographically valid!' : 
  '❌ Signature verification failed - signature may be forged or message altered.'}`
    }
    
    return 'Select a signature and click "Verify Signature" to check its validity.'
  }

  const signatureOptions = (txMessages || []).map((sig, index) => {
    const level = sig.wallet_id.split(',').length - 1
    const levelIcon = level === 0 ? '🏠' : '📁'.repeat(level)
    return {
      value: index,
      label: `${levelIcon} ${sig.id} - "${sig.message.substring(0, 30)}${sig.message.length > 30 ? '...' : ''}" (${sig.wallet_id})`
    }
  })

  const selectedSignature = selectedSigIndex !== '' && txMessages ? txMessages[parseInt(selectedSigIndex)] : null

  return (
    <Section title="✅ HDWSA Signature Verification">
      <div className="controls">
        <div className="input-group">
          <Select
            label="Select Signature to Verify:"
            value={selectedSigIndex}
            onChange={(e) => setSelectedSigIndex(e.target.value)}
            disabled={localLoading.verifying}
          >
            <option value="">Select a signature...</option>
            {signatureOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>

          {selectedSignature && (
            <div className="signature-info">
              <h4>Selected Signature Information:</h4>
              <div className="signature-details">
                <div className="detail-item">
                  <strong>Original Message:</strong> "{selectedSignature.message}"
                </div>
                <div className="detail-item">
                  <strong>Wallet:</strong> {selectedSignature.wallet_id}
                </div>
                <div className="detail-item">
                  <strong>h:</strong> {truncateHex(selectedSignature.h_hex)}
                </div>
                <div className="detail-item">
                  <strong>Q_sigma:</strong> {truncateHex(selectedSignature.Q_sigma_hex)}
                </div>
              </div>
            </div>
          )}

          <div className="verification-options">
            <label className="checkbox-option">
              <input
                type="checkbox"
                checked={useCustomMessage}
                onChange={(e) => setUseCustomMessage(e.target.checked)}
                disabled={localLoading.verifying}
              />
              Verify with custom message (test message tampering)
            </label>

            {useCustomMessage && (
              <Input
                label="Custom Message:"
                type="text"
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                placeholder="Enter custom message to test verification..."
                disabled={localLoading.verifying}
              />
            )}
          </div>
        </div>

        <div className="button-group">
          <Button
            onClick={handleVerifySignature}
            loading={localLoading.verifying}
            disabled={!selectedSigIndex || localLoading.verifying || (useCustomMessage && !customMessage.trim())}
          >
            ✅ Verify Signature
          </Button>
          
          <Button
            onClick={handleRefreshData}
            variant="secondary"
            loading={globalLoading.txMessages}
          >
            🔄 Refresh Signatures
          </Button>
        </div>
      </div>

      {(txMessages || []).length === 0 && (
        <div className="info-message">
          ℹ️ No signatures available. Please sign messages first.
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
          gap: 1rem;
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

        .signature-info {
          background: #e7f3ff;
          border: 1px solid #b3d9ff;
          border-radius: 4px;
          padding: 1rem;
        }

        .signature-info h4 {
          margin: 0 0 0.5rem 0;
          color: #0056b3;
          font-size: 14px;
        }

        .signature-details {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .detail-item {
          font-size: 13px;
          color: #495057;
        }

        .detail-item strong {
          color: #0056b3;
          min-width: 120px;
          display: inline-block;
        }

        .verification-options {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .checkbox-option {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 14px;
          color: #495057;
        }

        .checkbox-option input[type="checkbox"] {
          margin: 0;
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

export default HdwsaSignatureVerification