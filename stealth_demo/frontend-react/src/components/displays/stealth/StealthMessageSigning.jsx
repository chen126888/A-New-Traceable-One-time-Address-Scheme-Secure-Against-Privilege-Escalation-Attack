import React from 'react'

// Stealth 訊息簽章顯示組件
export const StealthMessageSigning = ({ signResult, error }) => {
  if (error) {
    return `Error: ${error}`
  }
  
  if (signResult) {
    return `✍️ Stealth Message Signed Successfully!
📊 Signature ID: ${signResult.sig_id}
🔐 DSK ID: ${signResult.dsk_id}
📝 Message: "${signResult.message}"

🔏 Signature Components:
📊 Q-Sigma (G1 Element):
📝 Preview: ${signResult.q_sigma_hex?.substring(0, 32)}...
📏 Size: ${Math.floor((signResult.q_sigma_hex?.length || 0) / 2)} bytes
🔢 Full Hex: ${signResult.q_sigma_hex}

🏷️ H Component (Zr Element):
📝 Preview: ${signResult.h_hex?.substring(0, 32)}...
📏 Size: ${Math.floor((signResult.h_hex?.length || 0) / 2)} bytes
🔢 Full Hex: ${signResult.h_hex}

💡 This signature can be verified using the stealth address components.
🔐 The signature is anonymous but traceable by the authority.

✅ Status: ${signResult.status}`
  }
  
  return 'Enter a message and select a DSK to sign with Stealth scheme...'
}