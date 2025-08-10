import React from 'react'

// Stealth DSK (一次性密鑰) 顯示組件
export const StealthDskDisplay = ({ dskResult, error }) => {
  if (error) {
    return `Error: ${error}`
  }
  
  if (dskResult) {
    return `🔐 Stealth DSK Generated Successfully!
📊 DSK ID: ${dskResult.dsk_id}
🏠 Address ID: ${dskResult.addr_id}
🔑 Key ID: ${dskResult.key_id}

🔐 One-time Secret Key (${dskResult.dsk.name}):
📝 Preview: ${dskResult.dsk.preview}
📏 Size: ${dskResult.dsk.size} bytes
🔢 Full Hex: ${dskResult.dsk.hex}

💡 This DSK can be used to sign messages for the associated stealth address.
⚠️  Keep this DSK secure - it's required for signing transactions!

✅ Status: ${dskResult.status}`
  }
  
  return 'Select an address and key, then click "Generate DSK" to create a one-time secret key...'
}