import React from 'react'
import { truncateHex } from '../../../utils/helpers'

// SITAIBA 密鑰顯示組件
export const KeyDisplay = ({ keys, selectedIndex }) => {
  if (selectedIndex >= 0 && keys[selectedIndex]) {
    const key = keys[selectedIndex]
    return `🔑 Key Details - ${key.id}
📄 Parameter File: ${key.param_file || 'Unknown'}
📊 Status: ${key.status}

🔓 Public Key A:
${key.A_hex}

🔓 Public Key B:
${key.B_hex}

🔐 Private Key a:
${key.a_hex}

🔐 Private Key b:
${key.b_hex}`
  }
  
  // 顯示最新生成的密鑰信息
  if (keys.length > 0) {
    const latestKey = keys[keys.length - 1]
    return `✅ Key Generated Successfully!
🆔 Key ID: ${latestKey.id}
🔓 Public Key A: ${truncateHex(latestKey.A_hex)}
🔓 Public Key B: ${truncateHex(latestKey.B_hex)}
🔐 Private Key a: ${truncateHex(latestKey.a_hex)}
🔐 Private Key b: ${truncateHex(latestKey.b_hex)}`
  }
  
  return ''
}

// SITAIBA 密鑰列表項目
export const KeyListItems = ({ keys, selectedIndex, onKeyClick }) => {
  return keys.map((key, index) => ({
    id: key.id,
    header: `${key.id} (${key.scheme})`,
    details: [
      `A: ${truncateHex(key.A_hex, 12)}`,
      `B: ${truncateHex(key.B_hex, 12)}`
    ],
    selected: index === selectedIndex,
    onClick: () => onKeyClick(index)
  }))
}