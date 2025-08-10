import React from 'react'

// Stealth 身份追蹤顯示組件
export const StealthIdentityTracing = ({ traceResult, error }) => {
  if (error) {
    return `Error: ${error}`
  }
  
  if (traceResult) {
    return `🔍 Stealth Identity Tracing Complete!
📊 Address ID: ${traceResult.addr_id}
🔑 Original Key ID: ${traceResult.original_key_id}

🕵️ Recovered Public Key B (${traceResult.recovered_B.name}):
📝 Preview: ${traceResult.recovered_B.preview}
📏 Size: ${traceResult.recovered_B.size} bytes
🔢 Full Hex: ${traceResult.recovered_B.hex}

🔍 Original Public Key B:
${traceResult.original_B || 'Not available'}

${traceResult.match ? '✅' : '❌'} Match: ${traceResult.match}

${traceResult.match ? 
  `🎯 IDENTITY TRACED SUCCESSFULLY!
✅ The recovered key matches the original key
🔐 The stealth address belongs to Key ID ${traceResult.original_key_id}
👤 Identity has been successfully de-anonymized` :
  `❌ TRACING INCONCLUSIVE!
⚠️  The recovered key does not match the expected original key
🤔 This could indicate a tracing error or data inconsistency
🔍 Further investigation may be needed`
}

💡 Note: Only the tracing authority with the private tracer key can perform this operation.

✅ Status: ${traceResult.status}`
  }
  
  return 'Select a stealth address to trace its identity...'
}