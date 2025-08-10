import React from 'react'
import { truncateHex } from '../../../utils/helpers'

// SITAIBA 身份追蹤顯示組件 - 不包含 C 欄位
export const TraceDisplay = ({ 
  traceResults, 
  selectedTraceIndex, 
  keys, 
  findMatchingKey,
  localError, 
  globalError 
}) => {
  const error = localError || globalError
  if (error) {
    return `Error: ${error}`
  }
  
  if (selectedTraceIndex >= 0 && traceResults[selectedTraceIndex]) {
    const trace = traceResults[selectedTraceIndex]
    const matchedKey = findMatchingKey(trace.recovered_b_hex)
    const inputAddr = trace.input_address
    
    return `🔍 Identity Tracing Results - Trace ${selectedTraceIndex}
📧 Traced Address: ${trace.address_id}
⏰ Traced at: ${trace.timestamp}
📊 Status: ${trace.status}

🔐 Recovered Identity:
B (Public Key): ${trace.recovered_b_hex}

📋 Original Address Information:
🏠 Address: ${inputAddr?.addr_hex}
🎲 R1: ${inputAddr?.r1_hex}
🎲 R2: ${inputAddr?.r2_hex}
👤 Claimed Owner: ${inputAddr?.key_id}

🔍 Trace Authority Analysis:
${trace.original_owner ? `
🎯 Original Owner Record:
   Key Index: ${trace.original_owner.key_index}
   Key ID: ${trace.original_owner.key_id}
   B_hex: ${trace.original_owner.B_hex}
` : ''}

🤝 Key Matching Results:
${matchedKey ? `
✅ IDENTITY CONFIRMED!
   Matched Key: ${matchedKey.id}
   Key Index: ${keys.indexOf(matchedKey)}
   Perfect Match: ${matchedKey.B_hex === trace.recovered_b_hex ? 'YES' : 'NO'}
` : `
⚠️ No matching key found in current key list
   This could mean:
   - Key was generated elsewhere
   - Key was deleted from the system
   - Address was created with external keys
`}

🔄 Perfect Match Status: ${trace.perfect_match ? '✅ YES' : '❌ NO'}
📊 Tracing Status: ${trace.status}`
  }
  
  // 顯示最新追蹤結果
  if (traceResults.length > 0) {
    const latestTrace = traceResults[traceResults.length - 1]
    const matchedKey = findMatchingKey(latestTrace.recovered_b_hex)
    
    return `✅ Identity Tracing Completed!
📧 Traced Address: ${latestTrace.address_id}
🔐 Recovered B: ${truncateHex(latestTrace.recovered_b_hex)}
🤝 Match Found: ${matchedKey ? `YES (${matchedKey.id})` : 'NO'}
🔄 Perfect Match: ${latestTrace.perfect_match ? 'YES' : 'NO'}
📊 Status: ${latestTrace.status}`
  }
  
  return 'Select an address to trace its identity...'
}

// SITAIBA 追蹤結果列表項目
export const TraceListItems = ({ traceResults, selectedTraceIndex, onTraceClick, findMatchingKey }) => {
  return traceResults.map((trace, index) => {
    const matchedKey = findMatchingKey(trace.recovered_b_hex)
    return {
      id: `trace_${index}`,
      header: `Trace ${index} (${trace.address_id})`,
      details: [
        `Recovered B: ${truncateHex(trace.recovered_b_hex, 12)}`,
        `Match: ${matchedKey ? matchedKey.id : 'None'}`,
        `Status: ${trace.perfect_match ? 'Perfect' : 'Partial'}`
      ],
      selected: index === selectedTraceIndex,
      onClick: () => onTraceClick(index)
    }
  })
}