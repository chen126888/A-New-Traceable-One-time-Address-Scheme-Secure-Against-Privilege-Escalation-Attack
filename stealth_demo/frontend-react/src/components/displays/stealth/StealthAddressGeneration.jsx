import React from 'react'

// Stealth 地址生成顯示組件
export const StealthAddressGeneration = ({ addressResult, error, verificationResult }) => {
  if (error) {
    return `Error: ${error}`
  }
  
  let output = ''
  
  if (addressResult) {
    output += `🏠 Stealth Address Generated Successfully!
📊 Address ID: ${addressResult.addr_id}
🔑 Using Key ID: ${addressResult.key_id}

🏠 Stealth Address (${addressResult.address.name}):
📝 Preview: ${addressResult.address.preview}
📏 Size: ${addressResult.address.size} bytes
🔢 Full Hex: ${addressResult.address.hex}

🎲 R1 Component (${addressResult.R1.name}):
📝 Preview: ${addressResult.R1.preview}
📏 Size: ${addressResult.R1.size} bytes
🔢 Full Hex: ${addressResult.R1.hex}

🎲 R2 Component (${addressResult.R2.name}):
📝 Preview: ${addressResult.R2.preview}
📏 Size: ${addressResult.R2.size} bytes
🔢 Full Hex: ${addressResult.R2.hex}

🔒 C Component (${addressResult.C.name}):
📝 Preview: ${addressResult.C.preview}
📏 Size: ${addressResult.C.size} bytes
🔢 Full Hex: ${addressResult.C.hex}

✅ Status: ${addressResult.status}`
  }
  
  if (verificationResult) {
    output += `

🔍 Address Verification Result:
📊 Address ID: ${verificationResult.addr_id}
🔑 Key ID: ${verificationResult.key_id}
${verificationResult.is_valid ? '✅' : '❌'} Valid: ${verificationResult.is_valid}
🔧 Method: ${verificationResult.verification_method}
✅ Status: ${verificationResult.status}`
  }
  
  return output || 'Select a key and click "Generate Address" to create a stealth address...'
}