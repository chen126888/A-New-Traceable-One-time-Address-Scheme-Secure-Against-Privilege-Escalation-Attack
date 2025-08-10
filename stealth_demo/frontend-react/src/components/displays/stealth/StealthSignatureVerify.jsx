import React from 'react'

// Stealth 交易簽章驗證顯示組件 (用於 transaction verification)
export const StealthSignatureVerify = ({ verifyResult, error }) => {
  if (error) {
    return `Error: ${error}`
  }
  
  if (verifyResult) {
    // 處理 transaction verification 的數據格式
    const isValid = verifyResult.valid ?? verifyResult.is_valid
    const message = verifyResult.transaction_data?.message || verifyResult.message
    const txData = verifyResult.transaction_data
    
    return `🔍 Stealth Transaction Verification Complete!
📝 Message: "${message}"
${isValid ? '✅' : '❌'} Valid: ${isValid}

📋 Transaction Components (addr, R, m, σ):
🏠 Address: ${txData?.address?.addr_hex?.substring(0, 20)}...
🎲 R2: ${txData?.address?.r2_hex?.substring(0, 20)}...
🔒 C: ${txData?.address?.c_hex?.substring(0, 20)}...
✍️ Q_sigma: ${txData?.signature?.q_sigma_hex?.substring(0, 20)}...
🔢 H: ${txData?.signature?.h_hex?.substring(0, 20)}...

${isValid ? 
  `🎉 Transaction is VALID!
✅ The signature was created with the correct DSK for this address
🔐 The message integrity has been verified
🏠 The signature matches the stealth address components` :
  `❌ Transaction is INVALID!
⚠️  The signature does not match the transaction components
🚫 Either the signature was tampered with or created with wrong DSK
❗ This transaction should not be trusted`
}

✅ Status: ${verifyResult.status}
⏰ Verified at: ${verifyResult.timestamp}`
  }
  
  return 'Select a transaction to verify its signature authenticity...'
}