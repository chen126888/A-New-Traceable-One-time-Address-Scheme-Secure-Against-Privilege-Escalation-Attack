import React from 'react'

// Stealth 系統設置顯示組件
export const StealthSystemSetup = ({ setupResult, error }) => {
  if (error) {
    return `Error: ${error}`
  }
  
  if (setupResult) {
    return `✅ Stealth System Setup Complete!
📄 Parameter File: ${setupResult.param_file}
🔧 Scheme: ${setupResult.scheme_name} v${setupResult.scheme_version}
📊 Status: ${setupResult.status}
🔑 Tracer Key: ${setupResult.tracer_key_available ? '✅ Available' : '❌ Not Available'}
📏 G1 Size: ${setupResult.g1_size} bytes
📏 Zr Size: ${setupResult.zr_size} bytes

🔐 Tracer Public Key (TK):
${setupResult.tracer_public_key}

🔒 Tracer Private Key (k):
${setupResult.tracer_private_key}

📏 Tracer Key Size: ${setupResult.tracer_key_size} bytes

${setupResult.message ? `💬 ${setupResult.message}` : ''}`
  }
  
  return 'Select a parameter file to initialize the Stealth system...'
}