import React from 'react'

// Stealth 金鑰生成顯示組件
export const StealthKeyGeneration = ({ keyResult, error }) => {
  if (error) {
    return `Error: ${error}`
  }
  
  if (keyResult) {
    return `🔑 Stealth Keypair Generated Successfully!
📊 Key ID: ${keyResult.key_id}
📏 Key Size: ${keyResult.key_size} bytes

🔓 Public Key A (${keyResult.public_key_A.name}):
📝 Preview: ${keyResult.public_key_A.preview}
📏 Size: ${keyResult.public_key_A.size} bytes
🔢 Full Hex: ${keyResult.public_key_A.hex}

🔓 Public Key B (${keyResult.public_key_B.name}):
📝 Preview: ${keyResult.public_key_B.preview}
📏 Size: ${keyResult.public_key_B.size} bytes
🔢 Full Hex: ${keyResult.public_key_B.hex}

🔐 Private Key a (${keyResult.private_key_a.name}):
📝 Preview: ${keyResult.private_key_a.preview}
📏 Size: ${keyResult.private_key_a.size} bytes
🔢 Full Hex: ${keyResult.private_key_a.hex}

🔐 Private Key b (${keyResult.private_key_b.name}):
📝 Preview: ${keyResult.private_key_b.preview}
📏 Size: ${keyResult.private_key_b.size} bytes
🔢 Full Hex: ${keyResult.private_key_b.hex}

✅ Status: ${keyResult.status}`
  }
  
  return 'Click "Generate Keypair" to create a new Stealth key pair...'
}