import React from 'react'

// SITAIBA 系統設置顯示組件
export const SystemSetupDisplay = ({ setupResult, error }) => {
  if (error) {
    return `Error: ${error}`
  }
  
  if (setupResult) {
    return `✅ SITAIBA System Setup Complete!
📄 Parameter File: ${setupResult.param_file}
🔧 Scheme: ${setupResult.scheme_name} v${setupResult.scheme_version}
📊 Status: ${setupResult.status}
🔑 Tracer Key: ${setupResult.tracer_key_available ? '✅ Available' : '❌ Not Available'}
📏 G1 Size: ${setupResult.g1_size} bytes
📏 Zr Size: ${setupResult.zr_size} bytes

🔐 Tracer Public Key A:
${setupResult.tracer_A_hex}

${setupResult.tracer_key_note ? `📝 Note: ${setupResult.tracer_key_note}` : ''}`
  }
  
  return 'Select a parameter file to initialize the SITAIBA system...'
}