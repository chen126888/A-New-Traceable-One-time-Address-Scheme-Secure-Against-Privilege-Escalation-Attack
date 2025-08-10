import React from 'react'
import { truncateHex } from '../../../utils/helpers'

// SITAIBA 地址顯示組件 - 不包含 C 欄位
export const AddressDisplay = ({ addresses, selectedIndex, onAddressClick, localError, globalError }) => {
  const error = localError || globalError
  if (error) {
    return `Error: ${error}`
  }
  
  if (selectedIndex >= 0 && addresses[selectedIndex]) {
    const addr = addresses[selectedIndex]
    return `🔍 Address Details - ${addr.id}
🆔 Index: ${selectedIndex}
👤 Owner Key: ${addr.key_id} (Index: ${addr.key_index})
📊 Status: ${addr.status}

🏠 Address:
${addr.addr_hex}

🎲 R1:
${addr.r1_hex}

🎲 R2:
${addr.r2_hex}`
  }
  
  // 顯示最新生成的地址信息
  if (addresses.length > 0) {
    const latestAddr = addresses[addresses.length - 1]
    return `✅ Address Generated Successfully!
🆔 Address ID: ${latestAddr.id}
👤 Owner Key: ${latestAddr.key_id}
🏠 Address: ${truncateHex(latestAddr.addr_hex)}
🎲 R1: ${truncateHex(latestAddr.r1_hex)}
🎲 R2: ${truncateHex(latestAddr.r2_hex)}`
  }
  
  return ''
}

// SITAIBA 地址列表項目 - 簡化顯示
export const AddressListItems = ({ addresses, selectedIndex, onAddressClick }) => {
  return addresses.map((addr, index) => ({
    id: addr.id,
    header: `${addr.id} (Owner: ${addr.key_id})`,
    details: [
      `${truncateHex(addr.addr_hex, 20)}`
    ],
    selected: index === selectedIndex,
    onClick: () => onAddressClick(index)
  }))
}