import React from 'react'
import { truncateHex } from '../../../utils/helpers'

// Stealth 地址驗證顯示組件
export const StealthAddressVerification = ({ verificationResult, addresses, keys, selectedAddrIndex, selectedKeyIndex, localError, globalError }) => {
  const error = localError || globalError
  if (error) {
    return `Error: ${error}`
  }
  
  if (verificationResult) {
    const selectedAddr = addresses[parseInt(selectedAddrIndex)]
    const selectedKey = keys[parseInt(selectedKeyIndex)]
    
    // For stealth: is_valid directly indicates ownership
    const addressId = verificationResult.addr_id ?? selectedAddrIndex
    const keyUsed = verificationResult.key_id ?? 'Unknown'
    const isOwner = verificationResult.is_valid ?? false
    
    return `🔍 Stealth Address Verification Results:
📧 Address: ${addressId}
🔑 Key Used: ${keyUsed}
👤 Is Owner: ${isOwner ? '✅ Yes' : '❌ No'}
📊 Status: ${verificationResult.status}

📋 Details:
🏠 Address: ${truncateHex(selectedAddr?.addr_hex)}
🔑 Key A: ${truncateHex(selectedKey?.A_hex)}
🔑 Key B: ${truncateHex(selectedKey?.B_hex)}

📧 Address Components:
🎲 R1: ${truncateHex(selectedAddr?.r1_hex)}
🎲 R2: ${truncateHex(selectedAddr?.r2_hex)}  
🎲 C: ${truncateHex(selectedAddr?.c_hex)}

${isOwner ? 
  '🎉 Perfect! This key is the owner of this address.' : 
  '❌ This key is not the owner of this address.'
}`
  }
  
  return ''
}