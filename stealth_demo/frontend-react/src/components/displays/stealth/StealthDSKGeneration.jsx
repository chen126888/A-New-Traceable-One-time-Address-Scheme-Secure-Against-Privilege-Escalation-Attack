import React from 'react'
import { truncateHex } from '../../../utils/helpers'

// Stealth DSK 生成顯示組件
export const StealthDSKGeneration = ({ dskList, selectedDSKIndex, onDSKClick, localError, globalError }) => {
  const error = localError || globalError
  if (error) {
    return `Error: ${error}`
  }
  
  if (selectedDSKIndex >= 0 && dskList[selectedDSKIndex]) {
    const dsk = dskList[selectedDSKIndex]
    // Handle stealth DSK format
    const dskId = dsk.id || `stealth_dsk_${dsk.dsk_id ?? selectedDSKIndex}`
    const addressId = dsk.address_id || (dsk.addr_id ?? 'Unknown')
    const keyId = dsk.key_id ?? 'Unknown'
    const dskHex = dsk.dsk_hex || dsk.dsk?.hex || 'Unknown'
    
    return `🔍 Stealth DSK Details - ${dskId}
🆔 Index: ${selectedDSKIndex}
📧 For Address: ${addressId}
🔑 Using Key: ${keyId}
📊 Status: ${dsk.status}

🔐 DSK (One-time Secret Key):
📝 Preview: ${truncateHex(dskHex, 24)}
📏 Size: ${dsk.dsk?.size || 20} bytes
🔢 Full Hex: ${dskHex}`
  }
  
  // 顯示最新生成的 DSK 信息
  if (dskList.length > 0) {
    const latestDSK = dskList[dskList.length - 1]
    // Handle stealth DSK format for latest DSK display
    const dskId = latestDSK.id || `stealth_dsk_${latestDSK.dsk_id ?? (dskList.length - 1)}`
    const addressId = latestDSK.address_id || (latestDSK.addr_id ?? 'Unknown')
    const keyId = latestDSK.key_id ?? 'Unknown'
    const dskHex = latestDSK.dsk_hex || latestDSK.dsk?.hex || 'Unknown'
    
    return `✅ Stealth DSK Generated Successfully!
🆔 DSK ID: ${dskId}
📧 For Address: ${addressId}
🔑 Using Key: ${keyId}
📊 Status: ${latestDSK.status}
🔐 DSK: ${truncateHex(dskHex)}`
  }
  
  return ''
}

// Stealth DSK List Items
export const StealthDSKListItems = ({ dskList, selectedIndex, onDSKClick }) => {
  if (!dskList || dskList.length === 0) return []
  
  return dskList.map((dsk, index) => {
    // Handle stealth DSK format for list items
    const dskId = dsk.id || `stealth_dsk_${dsk.dsk_id ?? index}`
    const addressId = dsk.address_id || (dsk.addr_id ?? 'Unknown')
    const keyId = dsk.key_id ?? 'Unknown'
    const dskHex = dsk.dsk_hex || dsk.dsk?.hex || 'Unknown'
    
    return {
      id: dskId,
      header: `${dskId} (Addr: ${addressId}, Key: ${keyId})`,
      details: [
        `DSK: ${truncateHex(dskHex, 16)}`
      ],
      selected: index === selectedIndex,
      onClick: () => onDSKClick(index)
    }
  })
}